// Actual pinned VM and fs implementation. Inputs/model selection/weather are
// explicit fixtures; this suite never claims an official native model session.
#[test]
fn stage3_group_execution_and_recovery() {
    let bundle=root().join("stage1/bundle");
    let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
    source.push_str(r#"
      fn s3_begin(id){ workflow_started=time_now() agent_task_kind="choice" begin_task(id) move("ANALYZING","Explicit SDK fixture") }
      fn s3_search_step(){ if coordinated_job != nil { search_step(coordinated_job) } }
      fn s3_finish(text){ finish_model(task_generation,text) }
      fn s3_report(){ fs.write("s3-state.json",{status:status busy:busy verified:verified proposal:proposal group:execution_group result:execution_result event:read_event()}.to_json()) }
      fn s3_edit(){ draft_changed() }
      fn s3_tamper(){ proposal.expected=proposal.expected.replace("Stage3 cycle","Unapproved title") }
      fn s3_expire(){ proposal.expires_at=time_now()-1 }
      fn s3_fixture_advice(text){ let raw=text.parse_json() let e=read_event() let c=option_for({plans:plan_entries(e) event:e search_id:"executor-fixture" sequence:1},raw.starts) workflow_started=time_now() active_task="s3-bounded-executor-fixture" planning_advice={before:schedule_fingerprint() weather_fingerprint:read_text("weather.json") expires_at:time_now()+500 candidate:c} busy=false move("PLAN_REVIEW","Explicit executor fixture; not an AI search result") }
    "#);
    let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
    let day=((now+28800)/86400+1)*86400-28800;
    let plan=|id:&str,title:&str,h:u64,movable:bool,target:u64|json!({"id":id,"title":title,"start":day+h*3600,"end":day+(h+1)*3600,"active":true,"movable":movable,"outdoor":false,"priority":3,"availability":if movable {json!({"min_start":day+target*3600,"max_end":day+(target+1)*3600})}else{Value::Null}});
    let original=json!({"schema":3,"event_id":"s3-primary","title":"Stage3 cycle","start":day+15*3600,"end":day+16*3600,"lat":22.54554,"lon":114.0683,"revision":1,"data_source":"ripple-local-activity","timezone":"UTC+08:00","location":null,"availability":{"min_start":day+9*3600,"max_end":day+10*3600},"planning":{"version":1,"instruction":"Synthetic controlled input","primary_movable":true,"priority":3,"preference":"morning","plans":[plan("meeting","Flexible meeting",12,true,14),plan("fixed-a","Fixed appointment",15,false,0),plan("fixed-b","Fixed meeting",12,false,0),plan("unrelated","Unrelated event",17,false,0)]}});
    let forecast=json!({"source":"FIXTURE","provider":"Open-Meteo","timezone":"GMT","utc_offset_seconds":0,"request_lat":22.54554,"request_lon":114.0683,"fetched_at":now,"revision":"s3-explicit-fixture","hours":(0..48).map(|h|json!({"start":day+h*3600,"end":day+(h+1)*3600,"code":0,"rain":0,"chance":0})).collect::<Vec<_>>()});
    let cases=["success","unapproved","decline","stale-plan","stale-after-approval","stale-weather","input-change","tamper","expired-approval","unsafe-order","cancel-before","cancel-between","write-denied","interrupted","unknown-readback","receipt-corrupt","concurrent-edit","concurrent-receipt","receipt-denied","three-step-partial"];
    let mut evidence_rows=Vec::new();
    // Optional selector isolates a fault case in its own process; assertions and
    // host budgets are identical, and default regression still runs every case.
    let selected=std::env::var("RIPPLE_STAGE3_CASE").ok();
    if let Some(ref selector)=selected { assert!(cases.contains(&selector.as_str()),"unknown Stage3 case selector"); }
    for case in cases.into_iter().filter(|case|selected.as_deref().map_or(true,|s|s==*case)) {
        eprintln!("STAGE3_CASE_BEGIN {case}");
        let (mut cx,_ui,card,reg,jail)=fixture(&format!("s3-{case}"),&source,&bundle);
        let schedule=jail.join("schedule.txt");let journal=jail.join("execution.json");
        let mut input=original.clone();
        if case=="three-step-partial" {input["planning"]["plans"]=json!([plan("m1","Flexible one",15,true,10),plan("m2","Flexible two",15,true,11),plan("fixed","Fixed appointment",15,false,0),plan("unrelated","Unrelated event",17,false,0)]);}
        if case=="unsafe-order" {input["planning"]["plans"]=json!([plan("swap","Swap meeting",9,true,15)]);}
        std::fs::write(&schedule,input.to_string()).unwrap();std::fs::write(jail.join("weather.json"),forecast.to_string()).unwrap();
        invoke(&mut cx,&card,id!(boot),&[]);
        let report=|cx:&mut Cx|{invoke(cx,&card,id!(s3_report),&[]);read(jail.join("s3-state.json"))};
        let call=|name:&str,args:Value,cx:&mut Cx|->Value{
            let replies:Replies=Default::default();let out=replies.clone();
            script_tools::submit("ripple",name,args,"device","stage3-fixture",Duration::from_secs(60),Box::new(move|r|out.lock().unwrap().push(r))).unwrap();pump(cx,&card);
            for _ in 0..1500 {if !replies.lock().unwrap().is_empty(){break;}invoke(cx,&card,id!(s3_search_step),&[]);pump(cx,&card);}
            let received=replies.lock().unwrap().first().cloned();
            let value=received.expect("bounded search finished").expect("valid tool result");value
        };
        if case=="unsafe-order" {
            let c=json!({"start":day+9*3600,"end":day+10*3600,"starts":[day+9*3600,day+15*3600]});
            invoke(&mut cx,&card,id!(s3_fixture_advice),&[&c.to_string()]);
        } else if case=="three-step-partial" {
            // Search intentionally remains primary + one related move. Exercise
            // the bounded executor's three-step recovery using an explicit
            // candidate fixture, never pass this off as planner/model evidence.
            let c=json!({"start":day+9*3600,"end":day+10*3600,"starts":[day+9*3600,day+10*3600,day+11*3600,day+15*3600,day+17*3600]});
            invoke(&mut cx,&card,id!(s3_fixture_advice),&[&c.to_string()]);
        } else {
            invoke(&mut cx,&card,id!(s3_begin),&[case]);
            let context=call("ripple.context.read",json!({"task_id":case}),&mut cx);
            let mut args=context["search_bounds"].clone();args["task_id"]=json!(case);args["read_token"]=context["read_token"].clone();
            let search=call("ripple.slots.search",args,&mut cx);
            let c=search["candidates"].as_array().unwrap().iter().find(|c|c["candidate_id"]==search["baseline_candidate_id"]).unwrap();
            assert_eq!(c["metrics"]["moved_count"],2);
            let choice=json!({"task_id":case,"read_token":context["read_token"],"decision":"PROPOSE","search_id":search["search_id"],"candidate_id":c["candidate_id"]});
            invoke(&mut cx,&card,id!(s3_finish),&[&choice.to_string()]);
        }
        assert_eq!(report(&mut cx)["status"],"PLAN_REVIEW");
        invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(&schedule),input,"advice does not grant approval");
        invoke(&mut cx,&card,id!(prepare_group),&[]);let preview=report(&mut cx);
        if case=="unsafe-order" {assert_eq!(preview["status"],"STALE");assert_eq!(read(&schedule),input);evidence_rows.push(json!({"case":case,"unsafe_order_rejected":true}));drop(reg);continue;}
        assert_eq!(preview["status"],"AWAITING_APPROVAL","{case}");
        let expected:Value=serde_json::from_str(preview["proposal"]["expected"].as_str().unwrap()).unwrap();
        let count=preview["proposal"]["steps"].as_array().unwrap().len();assert_eq!(count,if case=="three-step-partial"{3}else{2});
        if case=="unapproved" {invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(&schedule),input);evidence_rows.push(json!({"case":case,"unchanged":true}));drop(reg);continue;}
        if case=="decline" {invoke(&mut cx,&card,id!(decline),&[]);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(&schedule),input);evidence_rows.push(json!({"case":case,"unchanged":true}));drop(reg);continue;}
        if case=="stale-plan" {let mut changed=input.clone();changed["revision"]=json!(2);changed["planning"]["plans"][3]["start"]=json!(day+9*3600);changed["planning"]["plans"][3]["end"]=json!(day+10*3600);std::fs::write(&schedule,changed.to_string()).unwrap();}
        if case=="stale-weather" {let mut w=forecast.clone();w["fetched_at"]=json!(now-601);std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();}
        if case=="input-change" {invoke(&mut cx,&card,id!(s3_edit),&[]);}
        if case=="tamper" {invoke(&mut cx,&card,id!(s3_tamper),&[]);}
        if case=="expired-approval" {invoke(&mut cx,&card,id!(s3_expire),&[]);}
        let before_approve=std::fs::read(&schedule).unwrap();
        invoke(&mut cx,&card,id!(confirm),&[]);
        if case=="stale-after-approval" {let mut changed=input.clone();changed["revision"]=json!(2);changed["title"]=json!("Concurrent edit");std::fs::write(&schedule,changed.to_string()).unwrap();}
        if case=="cancel-before" {invoke(&mut cx,&card,id!(cancel_group),&[]);}
        if case=="receipt-denied" {
            // Existing receipt changed after approval must be detected first.
            std::fs::create_dir(&journal).unwrap();
        }
        invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(execute),&[]);
        if ["stale-plan","stale-after-approval","stale-weather","input-change","tamper","expired-approval","cancel-before"].contains(&case) {
            let state=report(&mut cx);assert!(state["status"]=="STALE"||state["status"]=="DECLINED","{case}: {state}");
            if case!="stale-after-approval" {assert_eq!(std::fs::read(&schedule).unwrap(),before_approve);}
            else {assert_eq!(read(&schedule)["title"],"Concurrent edit");}
            evidence_rows.push(json!({"case":case,"report":state,"no_execution":true}));drop(reg);continue;
        }
        if case=="receipt-denied" {
            invoke(&mut cx,&card,id!(finish_verify),&[]);assert_eq!(read(&schedule),input);assert_eq!(report(&mut cx)["status"],"PARTIAL");
            evidence_rows.push(json!({"case":case,"unchanged":true}));drop(reg);continue;
        }
        let first=std::fs::read(&schedule).unwrap();assert_ne!(first,before_approve);
        if case=="interrupted" {
            invoke(&mut cx,&card,id!(boot),&[]);let state=report(&mut cx);assert_eq!(state["status"],"PARTIAL");assert_eq!(state["result"]["checkpoint"],1);
            invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(std::fs::read(&schedule).unwrap(),first);
            evidence_rows.push(json!({"case":case,"after_restart":state,"no_replay":true}));drop(reg);continue;
        }
        if case=="unknown-readback" {
            std::fs::write(&schedule,"{truncated").unwrap();invoke(&mut cx,&card,id!(finish_verify),&[]);let state=report(&mut cx);assert_eq!(state["status"],"PARTIAL");assert_eq!(state["result"]["checkpoint"],-1);
            invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(std::fs::read(&schedule).unwrap(),b"{truncated");
            std::fs::write(&schedule,&first).unwrap();invoke(&mut cx,&card,id!(inspect_result),&[]);assert_eq!(report(&mut cx)["result"]["checkpoint"],1);
            evidence_rows.push(json!({"case":case,"unknown":state,"restored_fixture_reconciled":true}));drop(reg);continue;
        }
        if case=="receipt-corrupt" {
            std::fs::write(&journal,"{truncated").unwrap();invoke(&mut cx,&card,id!(finish_verify),&[]);assert_eq!(report(&mut cx)["status"],"PARTIAL");invoke(&mut cx,&card,id!(boot),&[]);assert_eq!(report(&mut cx)["status"],"PARTIAL");
            assert_eq!(std::fs::read(&journal).unwrap(),b"{truncated");assert_eq!(std::fs::read(&schedule).unwrap(),first);
            evidence_rows.push(json!({"case":case,"corrupt_original_preserved":true,"no_replay":true}));drop(reg);continue;
        }
        if case=="cancel-between" {invoke(&mut cx,&card,id!(cancel_group),&[]);}
        invoke(&mut cx,&card,id!(finish_verify),&[]);
        if case=="three-step-partial" {invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(finish_verify),&[]);}
        let checkpoint_bytes=std::fs::read(&schedule).unwrap();
        if case=="write-denied"||case=="three-step-partial" {let mut perms=schedule.metadata().unwrap().permissions();perms.set_readonly(true);std::fs::set_permissions(&schedule,perms).unwrap();}
        if case=="concurrent-edit" {let mut changed=read(&schedule);changed["revision"]=json!(30);changed["planning"]["plans"][3]["title"]=json!("External edit must survive");std::fs::write(&schedule,changed.to_string()).unwrap();}
        if case=="concurrent-receipt" {std::fs::write(&journal,"{\"kind\":\"SAVE\",\"operation_id\":\"other-writer\"}").unwrap();}
        invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(finish_verify),&[]);
        let final_state=report(&mut cx);
        if case=="success" {
            assert_eq!(final_state["status"],"COMPLETED");assert_eq!(read(&schedule),expected);assert_eq!(read(&journal)["status"],"COMPLETED");
            for i in 1..4 {assert_eq!(read(&schedule)["planning"]["plans"][i],input["planning"]["plans"][i]);}
            invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(&schedule),expected);
            invoke(&mut cx,&card,id!(boot),&[]);assert_eq!(report(&mut cx)["status"],"COMPLETED");assert_eq!(read(&schedule),expected);
        } else {
            assert_eq!(final_state["status"],"PARTIAL","{case}: {final_state}");assert_eq!(final_state["verified"],false);
            if case!="concurrent-edit" {assert_eq!(std::fs::read(&schedule).unwrap(),checkpoint_bytes);}
            if case=="concurrent-receipt" {assert_eq!(read(&journal)["operation_id"],"other-writer");}
            if case=="write-denied"||case=="three-step-partial" {
                let done=if case=="three-step-partial" {2}else{1};assert_eq!(final_state["result"]["checkpoint"],done);
                assert_eq!(final_state["result"]["results"][done as usize]["state"],"FAILED");
                let mut perms=schedule.metadata().unwrap().permissions();perms.set_readonly(false);std::fs::set_permissions(&schedule,perms).unwrap();
                invoke(&mut cx,&card,id!(boot),&[]);assert_eq!(report(&mut cx)["status"],"PARTIAL");
                invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(std::fs::read(&schedule).unwrap(),checkpoint_bytes);
                invoke(&mut cx,&card,id!(close_group_result),&[]);assert_eq!(report(&mut cx)["status"],"FAILED");assert_eq!(read(&journal)["closed"],true);
                invoke(&mut cx,&card,id!(boot),&[]);assert_eq!(report(&mut cx)["status"],"FAILED");
            }
        }
        evidence_rows.push(json!({"case":case,"before":input,"approved":preview["proposal"],"result":final_state,"actual":read(&schedule)}));drop(reg);
    }
    write("stage3-execution-results.json",&json!({"classification":"ACTUAL_PINNED_VM_STORAGE_AND_APPTOOLS_EXPLICIT_FIXTURES","cases":evidence_rows}));
}
