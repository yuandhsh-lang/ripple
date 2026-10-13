// Real pinned VM and AppTools ABI. Model/weather bodies here are explicit fixtures.
#[test]
fn stage2_interpretation_coordination_and_guards() {
    let bundle=root().join("bundle");
    let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
    source.push_str(r#"
      fn s2_setup(epoch){ busy=false loading=false status="READY" agent_task_kind="choice" planning_draft=nil manual_location=true selected_city=nil ui.title_input.set_text("Synthetic cycle") ui.start_input.set_text(local_date(epoch.to_f64())+" "+local_clock(epoch.to_f64())) ui.duration.set_text("60") ui.latitude.set_text("22.54554") ui.longitude.set_text("114.0683") ui.available_start.set_text("09:00") ui.available_end.set_text("17:00") let before=schedule_fingerprint() save_activity() finish_save(before,false) }
      fn s2_meta(text){ planning_draft=text.parse_json() let before=schedule_fingerprint() busy=false status="READY" save_activity() finish_save(before,false) }
      fn s2_begin(kind){ busy=false loading=false agent_task_kind=kind interpret_text=ui.intent_input.text() workflow_started=time_now() begin_task("s2-task") move("ANALYZING","Explicit SDK fixture, not a real model") }
      fn s2_step(){ if coordinated_job != nil { search_step(coordinated_job) } }
      fn s2_finish(text){ finish_model(task_generation,text) }
      fn s2_report(){ fs.write("s2-state.json",{status:status message:message event:read_event() draft:interpretation_draft planning:planning_draft advice:planning_advice proposal:proposal search:last_search dirty:dirty}.to_json()) }
      fn s2_clock(epoch){ fs.write("s2-clock.json",{text:local_date(epoch.to_f64())+" "+local_clock(epoch.to_f64())}.to_json()) }
      fn s2_edit(){ draft_changed() }
      fn s2_cache(now){ let good=read_weather_snapshot(read_event(),now.to_f64()) fs.write("s2-cache.json",{accepted:good!=nil}.to_json()) }
    "#);
    let (mut cx,_ui,card,reg,jail)=fixture("stage2-jail",&source,&bundle);
    let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();let day=((now+28800)/86400+1)*86400-28800;
    let report=|cx:&mut Cx|{invoke(cx,&card,id!(s2_report),&[]);read(jail.join("s2-state.json"))};
    let clock=|epoch:u64,cx:&mut Cx|{invoke(cx,&card,id!(s2_clock),&[&epoch.to_string()]);read(jail.join("s2-clock.json"))["text"].as_str().unwrap().to_owned()};
    invoke(&mut cx,&card,id!(s2_setup),&[&(day+15*3600).to_string()]);
    let original=read(jail.join("schedule.txt"));assert_eq!(original["schema"],3);
    let weather=|rain:bool|json!({"source":"FIXTURE","provider":"Open-Meteo","timezone":"GMT","utc_offset_seconds":0,"request_lat":22.54554,"request_lon":114.0683,"fetched_at":now,"revision":"stage2-explicit-fixture","hours":(0..24).map(|h|json!({"start":day+h*3600,"end":day+(h+1)*3600,"code":if rain&&h==15{61}else{0},"rain":if rain&&h==15{2}else{0},"chance":if rain&&h==15{80}else{0}})).collect::<Vec<_>>()});
    let install=|w:&Value|std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();install(&weather(true));
    let call=|name:&str,args:Value,cx:&mut Cx|->Value{
        let replies:Replies=Default::default();let out=replies.clone();
        script_tools::submit("ripple",name,args,"device","stage2-protocol-fixture",Duration::from_secs(60),Box::new(move|r|out.lock().unwrap().push(r))).unwrap();pump(cx,&card);
        // 49 primary slots * (4 * 49 related slots + cursor steps), 16 steps
        // per callback. This is a work bound, not a relaxed host time budget.
        for _ in 0..1500 { if !replies.lock().unwrap().is_empty(){break} invoke(cx,&card,id!(s2_step),&[]);pump(cx,&card); }
        let answer=replies.lock().unwrap().first().cloned().expect("bounded async search completed").expect("schema-valid AppTools result");answer
    };
    let start_text=clock(day+15*3600,&mut cx);
    let draft_plan=|id:&str,title:&str,start:u64,end:u64,movable:bool,left:&str,right:&str,cx:&mut Cx|json!({"id":id,"title":title,"city_query":"深圳","start_text":clock(start,cx),"end_text":clock(end,cx),"active":true,"movable":movable,"outdoor":false,"priority":5,"window_start":left,"window_end":right});
    let draft=json!({"title":"Synthetic cycle","city_query":"深圳","start_text":start_text,"duration_minutes":60,"window_start":"09:00","window_end":"17:00","primary_movable":true,"priority":3,"preference":"morning","plans":[draft_plan("meeting","Fixed meeting",day+9*3600,day+10*3600,false,"","",&mut cx),draft_plan("medical","Fixed appointment",day+11*3600,day+12*3600,false,"","",&mut cx)]});
    invoke(&mut cx,&card,id!(s2_begin),&["interpret"]);let input=call("ripple.context.read",json!({"task_id":"s2-task"}),&mut cx);assert_eq!(input["mode"],"interpret");
    let reply=json!({"task_id":"s2-task","read_token":input["read_token"],"decision":"DRAFT","draft":draft});
    invoke(&mut cx,&card,id!(s2_finish),&[&reply.to_string()]);let interpreted=report(&mut cx);assert_eq!(interpreted["status"],"DRAFT_REVIEW");assert_eq!(read(jail.join("schedule.txt")),original);
    invoke(&mut cx,&card,id!(s2_begin),&["interpret"]);let fenced_ctx=call("ripple.context.read",json!({"task_id":"s2-task"}),&mut cx);let mut fenced_reply=reply.clone();fenced_reply["read_token"]=fenced_ctx["read_token"].clone();
    invoke(&mut cx,&card,id!(s2_finish),&[&format!("```json\n{}\n```",fenced_reply)]);assert_eq!(report(&mut cx)["status"],"DRAFT_REVIEW","an exact outer JSON fence must not strand the UI");assert_eq!(read(jail.join("schedule.txt")),original);
    for bad_text in ["{bad","{}","{\"task_id\":\"s2-task\",\"read_token\":\"missing\",\"draft\":{},\"question\":\"x\"}"] {
        invoke(&mut cx,&card,id!(s2_begin),&["interpret"]);invoke(&mut cx,&card,id!(s2_finish),&[bad_text]);assert_eq!(report(&mut cx)["status"],"FAILED","malformed model output must terminate without a field trap");assert_eq!(read(jail.join("schedule.txt")),original);
    }
    invoke(&mut cx,&card,id!(s2_begin),&["interpret"]);let city_ctx=call("ripple.context.read",json!({"task_id":"s2-task"}),&mut cx);let mut other_city=reply.clone();other_city["read_token"]=city_ctx["read_token"].clone();other_city["draft"]["plans"][0]["city_query"]=json!("上海");invoke(&mut cx,&card,id!(s2_finish),&[&other_city.to_string()]);assert_eq!(report(&mut cx)["status"],"FAILED");assert_eq!(read(jail.join("schedule.txt")),original);
    invoke(&mut cx,&card,id!(s2_begin),&["interpret"]);let valid_ctx=call("ripple.context.read",json!({"task_id":"s2-task"}),&mut cx);let mut valid_reply=reply.clone();valid_reply["read_token"]=valid_ctx["read_token"].clone();invoke(&mut cx,&card,id!(s2_finish),&[&valid_reply.to_string()]);assert_eq!(report(&mut cx)["status"],"DRAFT_REVIEW");
    invoke(&mut cx,&card,id!(apply_interpretation),&[]);assert_eq!(read(jail.join("schedule.txt")),original,"Apply fills a draft, never saves");let meta=report(&mut cx)["planning"].clone();
    // A synthetic explicit save uses the already tested coordinate fallback.
    invoke(&mut cx,&card,id!(s2_setup),&[&(day+15*3600).to_string()]);invoke(&mut cx,&card,id!(s2_meta),&[&meta.to_string()]);let saved=read(jail.join("schedule.txt"));assert_eq!(saved["planning"],meta);
    let search=|cx:&mut Cx|->(Value,Value){
        invoke(cx,&card,id!(s2_begin),&["choice"]);let context=call("ripple.context.read",json!({"task_id":"s2-task"}),cx);let mut args=context["search_bounds"].clone();args["task_id"]=json!("s2-task");args["read_token"]=context["read_token"].clone();let found=call("ripple.slots.search",args,cx);(context,found)
    };
    let (context,candidates)=search(&mut cx);assert_eq!(context["impact"]["conflict"],true);assert!(!candidates["candidates"].as_array().unwrap().is_empty());
    for c in candidates["candidates"].as_array().unwrap(){
        assert_eq!(c["metrics"]["moved_count"],1);assert_eq!(c["related_changes"],json!([]));let s=c["start"].as_u64().unwrap();let end=c["end"].as_u64().unwrap();
        for a in saved["planning"]["plans"].as_array().unwrap(){assert!(!(s<a["end"].as_u64().unwrap()&&a["start"].as_u64().unwrap()<end),"fixed plan conflict");}
    }
    let chosen=candidates["candidates"].as_array().unwrap().iter().find(|c|c["metrics"]["preference_penalty"]==0).expect("morning preference has a valid slot");
    let choice=json!({"task_id":"s2-task","read_token":context["read_token"],"decision":"PROPOSE","search_id":candidates["search_id"],"candidate_id":chosen["candidate_id"]});
    invoke(&mut cx,&card,id!(s2_finish),&[&choice.to_string()]);assert_eq!(report(&mut cx)["status"],"AWAITING_APPROVAL");assert_eq!(read(jail.join("schedule.txt")),saved);
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(finish_verify),&[]);assert_eq!(report(&mut cx)["status"],"COMPLETED");let after=read(jail.join("schedule.txt"));assert_eq!(after["planning"],saved["planning"]);assert_eq!(after["start"],chosen["start"]);
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),after);
    // Related-only conflict: primary stays fixed; one flexible meeting can move.
    invoke(&mut cx,&card,id!(s2_setup),&[&(day+15*3600).to_string()]);install(&weather(false));let mut linked=meta.clone();linked["primary_movable"]=json!(false);linked["preference"]=json!("none");
    linked["plans"][0]["start"]=json!(day+15*3600);linked["plans"][0]["end"]=json!(day+16*3600);linked["plans"][0]["movable"]=json!(true);linked["plans"][0]["availability"]=json!({"min_start":day+14*3600,"max_end":day+17*3600});
    invoke(&mut cx,&card,id!(s2_meta),&[&linked.to_string()]);let linked_before=read(jail.join("schedule.txt"));let (lc,ls)=search(&mut cx);assert_eq!(lc["impact"]["conflict"],true);let candidate=&ls["candidates"][0];assert_eq!(candidate["start"],day+15*3600);assert_eq!(candidate["related_changes"].as_array().unwrap().len(),1);
    let choose=json!({"task_id":"s2-task","read_token":lc["read_token"],"decision":"PROPOSE","search_id":ls["search_id"],"candidate_id":candidate["candidate_id"]});invoke(&mut cx,&card,id!(s2_finish),&[&choose.to_string()]);let advice=report(&mut cx);assert_eq!(advice["status"],"PLAN_REVIEW");assert!(advice["proposal"].is_null());invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),linked_before);
    invoke(&mut cx,&card,id!(s2_edit),&[]);assert_eq!(report(&mut cx)["status"],"STALE");
    // Fixing the overlapping meeting leaves no legal option; never override it.
    linked["plans"][0]["movable"]=json!(false);invoke(&mut cx,&card,id!(s2_meta),&[&linked.to_string()]);let (_,none)=search(&mut cx);assert_eq!(none["candidates"],json!([]));
    // Explicit cancellation remains stored and removes only that conflict.
    linked["plans"][0]["active"]=json!(false);invoke(&mut cx,&card,id!(s2_meta),&[&linked.to_string()]);let (clear,keep)=search(&mut cx);assert_eq!(clear["impact"]["conflict"],false);assert_eq!(keep["candidates"][0]["metrics"]["moved_count"],0);assert_eq!(read(jail.join("schedule.txt"))["planning"]["plans"].as_array().unwrap().len(),2);
    // Dropping an existing plan from an AI draft is rejected, never data loss.
    invoke(&mut cx,&card,id!(s2_begin),&["interpret"]);let ctx=call("ripple.context.read",json!({"task_id":"s2-task"}),&mut cx);let mut bad=reply.clone();bad["read_token"]=ctx["read_token"].clone();bad["draft"]["plans"]=json!([]);let before_bad=read(jail.join("schedule.txt"));invoke(&mut cx,&card,id!(s2_finish),&[&bad.to_string()]);assert_eq!(report(&mut cx)["status"],"FAILED");assert_eq!(read(jail.join("schedule.txt")),before_bad);
    // Cache must not weaken byte-change, age or coordinate validation.
    install(&weather(false));invoke(&mut cx,&card,id!(s2_cache),&[&now.to_string()]);assert_eq!(read(jail.join("s2-cache.json"))["accepted"],true);
    invoke(&mut cx,&card,id!(s2_cache),&[&(now+601).to_string()]);assert_eq!(read(jail.join("s2-cache.json"))["accepted"],false);
    let mut corrupt=weather(false);corrupt["hours"][3]["end"]=json!(0);install(&corrupt);invoke(&mut cx,&card,id!(s2_cache),&[&now.to_string()]);assert_eq!(read(jail.join("s2-cache.json"))["accepted"],false);
    // Max supported plan count and forecast length: unresolved overlap cannot
    // cause a long blocking callback or invent a solution outside search scope.
    let mut max_weather=weather(false);max_weather["hours"]=json!((0..168).map(|h|json!({"start":day+h*3600,"end":day+(h+1)*3600,"code":0,"rain":0,"chance":0})).collect::<Vec<_>>());install(&max_weather);
    let mut stress=linked.clone();stress["primary_movable"]=json!(true);stress["plans"]=json!((0..4).map(|i|json!({"id":format!("stress-{i}"),"title":"Synthetic flexible overlap","start":day+15*3600,"end":day+16*3600,"active":true,"movable":true,"outdoor":false,"priority":3,"availability":{"min_start":day,"max_end":day+23*3600}})).collect::<Vec<_>>());
    invoke(&mut cx,&card,id!(s2_meta),&[&stress.to_string()]);let stress_before=read(jail.join("schedule.txt"));let (_,stress_result)=search(&mut cx);assert_eq!(stress_result["candidates"],json!([]));assert_eq!(read(jail.join("schedule.txt")),stress_before);
    write("stage2-planning.json",&json!({"classification":"ACTUAL_PINNED_VM_AND_APPTOOLS_EXPLICIT_MODEL_WEATHER_FIXTURES","interpreted_draft":interpreted,"context":context,"candidates":candidates,"single_execution_readback":after,"related_only_advice":advice,"no_solution":none,"cancelled_plan_preserved":clear,"unchanged_plan":keep,"cache_expiry_and_content_guards":true,"duplicate_execution_unchanged":true,"missing_existing_plan_rejected":true}));
    drop(reg);
}
