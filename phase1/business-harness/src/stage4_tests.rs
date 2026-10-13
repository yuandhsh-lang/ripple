// Actual VM/tools/storage; synthetic plans, weather replay and model selection.
#[test]
fn stage4_change_response_and_existing_execution() {
    let bundle=root().join("stage1/bundle");
    let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
    source.push_str(r#"
      fn s4_check(){ finish_change_check("sdk_replay",input_generation,schedule_fingerprint()) }
      fn s4_facts(){ let e=read_event() let w=read_weather_snapshot(e,time_now()) weather=w.hours fs.write("facts.json",change_facts(e).to_json()) }
      fn s4_card(){ fs.write("glance-payload.json",{payload:glance_payload()}.to_json()) }
      fn s4_report(){ fs.write("state.json",{status:status busy:busy verified:verified change:change_context message:message mode:planning_mode change_message:change_message}.to_json()) }
      fn s4_outage(){ change_agent_failed(task_generation,"EXPLICIT_SDK_PROVIDER_OUTAGE") }
      fn s4_rule_begin(){ preview_candidates() }
      fn s4_rule_search(){ preview_search(task_generation,input_generation) }
      fn s4_begin(){ agent_task_kind="choice" workflow_started=time_now() begin_task("s4-change") move("ANALYZING","EXPLICIT MODEL FIXTURE") }
      fn s4_search(){ if coordinated_job != nil { search_step(coordinated_job) } }
      fn s4_finish(text){ finish_model(task_generation,text) }
      fn s4_partial(){ busy=false move("PARTIAL","EXPLICIT UNKNOWN RESULT FIXTURE") }
    "#);
    let (mut cx,_ui,card,reg,jail)=fixture("s4-change",&source,&bundle);
    let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
    let day=((now+28800)/86400+1)*86400-28800;
    let primary=json!({"schema":3,"event_id":"cycle","title":"骑行","start":day+9*3600,"end":day+11*3600,"lat":22.54554,"lon":114.0683,"revision":1,"data_source":"ripple-local-activity","timezone":"UTC+08:00","location":null,"availability":{"min_start":day+8*3600,"max_end":day+12*3600},"planning":{"version":1,"instruction":"Explicit fixture","primary_movable":true,"priority":3,"preference":"morning","plans":[]}});
    let mut weather=json!({"source":"FIXTURE","provider":"Open-Meteo","timezone":"GMT","utc_offset_seconds":0,"request_lat":22.54554,"request_lon":114.0683,"fetched_at":now,"revision":"s4-weather","hours":(0..48).map(|h|json!({"start":day+h*3600,"end":day+(h+1)*3600,"code":0,"rain":0,"chance":0})).collect::<Vec<_>>()});
    let save=|name:&str,value:&Value|std::fs::write(jail.join(name),value.to_string()).unwrap();
    save("schedule.txt",&primary);save("weather.json",&weather);invoke(&mut cx,&card,id!(boot),&[]);
    let report=|cx:&mut Cx|{invoke(cx,&card,id!(s4_report),&[]);read(jail.join("state.json"))};
    invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(report(&mut cx)["status"],"NO_CHANGE");
    let baseline=read(jail.join("change-response.json"));
    weather["fetched_at"]=json!(now-1);weather["revision"]=json!("timestamp-only");weather["hours"][9]["rain"]=json!(0.2);save("weather.json",&weather);
    invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(read(jail.join("change-response.json")),baseline,"semantic weather jitter must remain quiet");
    let mut added=primary.clone();added["revision"]=json!(2);added["planning"]["plans"]=json!([
        {"id":"new-meeting","title":"十点固定会议","start":day+10*3600,"end":day+11*3600,"active":true,"movable":false,"outdoor":false,"priority":5,"availability":null},
        {"id":"unrelated","title":"下午会议","start":day+15*3600,"end":day+16*3600,"active":true,"movable":false,"outdoor":false,"priority":3,"availability":null}]);
    save("schedule.txt",&added);invoke(&mut cx,&card,id!(s4_check),&[]);let detected=report(&mut cx);assert_eq!(detected["status"],"RISK");assert_eq!(detected["change"]["affected"].as_array().unwrap().len(),2);assert_eq!(read(jail.join("schedule.txt")),added);
    invoke(&mut cx,&card,id!(s4_card),&[]);let risk_card=read(jail.join("glance-payload.json"));
    assert!(risk_card["payload"].is_object());assert!(risk_card["payload"]["title"].as_str().unwrap().contains("测试天气重放"));assert!(!risk_card["payload"]["summary"].as_str().unwrap().contains("骑行"),"public summary must not expose activity titles");
    let call=|name:&str,args:Value,cx:&mut Cx|->Value{
        let replies:Replies=Default::default();let out=replies.clone();
        script_tools::submit("ripple",name,args,"device","stage4-fixture",Duration::from_secs(60),Box::new(move|r|out.lock().unwrap().push(r))).unwrap();pump(cx,&card);
        for _ in 0..1500 {if !replies.lock().unwrap().is_empty(){break;}invoke(cx,&card,id!(s4_search),&[]);pump(cx,&card);}
        let received=replies.lock().unwrap().first().cloned();received.expect("search finished").expect("valid tool result")
    };
    let propose=|cx:&mut Cx|->(Value,Value){
        invoke(cx,&card,id!(s4_begin),&[]);let context=call("ripple.context.read",json!({"task_id":"s4-change"}),cx);let mut args=context["search_bounds"].clone();args["task_id"]=json!("s4-change");args["read_token"]=context["read_token"].clone();let search=call("ripple.slots.search",args,cx);
        let choice=json!({"task_id":"s4-change","read_token":context["read_token"],"decision":"PROPOSE","search_id":search["search_id"],"candidate_id":search["candidates"][0]["candidate_id"]});invoke(cx,&card,id!(s4_finish),&[&choice.to_string()]);(context,search)
    };
    invoke(&mut cx,&card,id!(s4_begin),&[]);let before_busy=report(&mut cx);
    invoke(&mut cx,&card,id!(interpret_input),&[]);let after_busy=report(&mut cx);
    assert_eq!(after_busy["change"],before_busy["change"],"a busy repeat click must preserve the active change explanation");
    let (context,search)=propose(&mut cx);assert!(context["change"].is_object());assert_eq!(report(&mut cx)["status"],"AWAITING_APPROVAL");
    assert_eq!(read(jail.join("schedule.txt")),added);invoke(&mut cx,&card,id!(decline),&[]);assert_eq!(read(jail.join("change-response.json"))["outcome"],"DECLINED");
    invoke(&mut cx,&card,id!(s4_card),&[]);assert!(read(jail.join("glance-payload.json"))["payload"].is_null(),"declined risk must withdraw its card");
    invoke(&mut cx,&card,id!(boot),&[]);invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(read(jail.join("change-response.json"))["outcome"],"DECLINED");assert_eq!(read(jail.join("schedule.txt")),added);
    // Explicit retry is allowed. Stale authorization still cannot write.
    propose(&mut cx);let mut edited=added.clone();edited["revision"]=json!(3);edited["availability"]["min_start"]=json!(day+9*3600);save("schedule.txt",&edited);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(report(&mut cx)["status"],"STALE");assert_eq!(read(jail.join("schedule.txt")),edited);
    save("schedule.txt",&added);propose(&mut cx);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(finish_verify),&[]);let after=read(jail.join("schedule.txt"));assert_eq!(report(&mut cx)["status"],"COMPLETED");assert_eq!(after["planning"],added["planning"]);assert_eq!(after["start"],day+8*3600);assert_eq!(after["revision"],3);
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),after);
    // Weather replay: dry -> wet matters, revision-only update doesn't.
    invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(report(&mut cx)["status"],"NO_CHANGE");
    weather["hours"][8]["chance"]=json!(80);save("weather.json",&weather);invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(report(&mut cx)["status"],"RISK");let wet=read(jail.join("change-response.json"));
    weather["fetched_at"]=json!(now-2);weather["revision"]=json!("another timestamp");save("weather.json",&weather);invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(read(jail.join("change-response.json")),wet);
    invoke(&mut cx,&card,id!(s4_outage),&[]);let fallback=report(&mut cx);assert_eq!(fallback["mode"],"user");assert!(fallback["change_message"].as_str().unwrap().contains("降级"));
    invoke(&mut cx,&card,id!(s4_rule_begin),&[]);invoke(&mut cx,&card,id!(s4_rule_search),&[]);
    for _ in 0..40 {invoke(&mut cx,&card,id!(s4_search),&[]);}
    assert_eq!(report(&mut cx)["status"],"NO_CANDIDATE");assert_eq!(read(jail.join("schedule.txt")),after,"fallback cannot write or fabricate a legal option");
    invoke(&mut cx,&card,id!(s4_partial),&[]);let mut changed=after.clone();changed["availability"]["max_end"]=json!(day+13*3600);save("schedule.txt",&changed);invoke(&mut cx,&card,id!(s4_check),&[]);assert_eq!(report(&mut cx)["status"],"PARTIAL");assert_eq!(read(jail.join("change-response.json")),wet);
    invoke(&mut cx,&card,id!(boot),&[]);weather["fetched_at"]=json!(now-601);save("weather.json",&weather);invoke(&mut cx,&card,id!(s4_check),&[]);assert_ne!(report(&mut cx)["status"],"NO_CHANGE");assert_eq!(read(jail.join("schedule.txt")),changed);
    write("stage4-change-response.json",&json!({"classification":"ACTUAL_VM_TOOLS_STORAGE_EXPLICIT_WEATHER_MODEL_FIXTURES","detected":detected,"context":context,"search":search,"independent_readback":after,"receipt":read(jail.join("execution.json")),"no_change_dedup":true,"decline_restart_dedup":true,"stale_rejected":true,"weather_replay_detected":true,"partial_blocks_analysis":true,"expired_weather_not_safe":true,"provider_outage_rule_fallback":fallback,"no_legal_candidate_does_not_write":true}));
    drop(reg);
}
