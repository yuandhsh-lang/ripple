//! Actual RC2-pinned script-tool queue/VM tests; no model or Shell installation claim.
#[cfg(test)]
mod tests {
    use makepad_widgets::*;
    use makepad_widgets::widget_tree::CxWidgetExt;
    use octosense_appstore::script_tools;
    use serde_json::{json, Value};
    use std::{path::{Path, PathBuf}, sync::{Arc, Mutex}, time::Duration};

    type Replies = Arc<Mutex<Vec<Result<Value, String>>>>;
    fn root() -> PathBuf { PathBuf::from(std::env::var("RIPPLE_TEST_ROOT").unwrap()) }
    fn evidence() -> PathBuf { PathBuf::from(std::env::var("RIPPLE_TEST_EVIDENCE").unwrap()) }
    fn write(name: &str, v: &Value) {
        let p=evidence().join(name);
        assert!(!p.exists(), "preserve previous evidence");
        std::fs::write(p, serde_json::to_vec_pretty(v).unwrap()).unwrap();
    }
    fn read(p: impl AsRef<Path>) -> Value { serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap() }
    fn fixture(label: &str, source: &str, reference: &Path) -> (Cx, WidgetRef, SplashRef, script_tools::Registration, PathBuf) {
        // Public isolate registration, identical app_tools implementation; no gate edits.
        makepad_widgets::widget_async::register_splash_isolate_mod(script_tools::script_mod);
        let mut cx=Cx::new(Box::new(|_,_|{}));
        let ui=cx.with_vm(|vm| {
            makepad_widgets::script_mod(vm);
            let value=script_eval!(vm,{use mod.prelude.widgets.* View{width:Fill height:Fill card:=Splash{width:Fill height:Fill}}});
            WidgetRef::script_from_value(vm,value)
        });
        let card=ui.splash(&mut cx,ids!(card));
        let jail=evidence().join(label);
        std::fs::create_dir(&jail).unwrap();
        card.set_host_tag(&mut cx,Some("ripple".into()));
        card.set_sandbox_dir(&mut cx,Some(jail.clone()));
        card.set_policy(&mut cx,Some(vec![]),Some(2_000_000));
        card.set_text(&mut cx,source);
        widget_tree::set_ui_root(&mut cx,&ui);
        // Mount/draw the real widget tree, as official card_layout_tests do.
        // app_tool legitimately calls ui.call.set_text; keep that UI code intact.
        {
        let pass=DrawPass::new(&mut cx);
        let size=dvec2(1200.0,1000.0);
        pass.set_size(&mut cx,size);
        let mut list=DrawList2d::new(&mut cx);
        let event=DrawEvent::default();
        let mut draw=makepad_draw::cx_draw::CxDraw::new(&mut cx,&event);
        let mut draw=Cx2d::new(&mut draw);
        draw.begin_pass(&pass,None);
        list.begin_always(&mut draw);
        draw.begin_root_turtle(size,Layout::default());
        ui.draw_walk_all(&mut draw,&mut Scope::empty(),Walk::abs_rect(Rect{pos:dvec2(0.0,0.0),size}));
        draw.end_turtle();
        list.end(&mut draw);
        draw.end_pass(&pass);
        }
        // Prime the lazy tree while Splash is unborrowed (native snapshots do this).
        let names=cx.widget_tree().compact_dump(&cx);
        std::fs::write(jail.join("mounted-widget-tree.txt"),names).unwrap();
        assert_eq!(cx.widget_tree().find_all_anywhere_including_skipped(ids!(call)).len(),1);
        // This private protocol fixture is digest-checked, never installed/published.
        let bundle=jail.join("protocol-fixture-bundle");
        std::fs::create_dir(&bundle).unwrap();
        for f in ["tools.json","AGENT.md"] { std::fs::copy(reference.join(f),bundle.join(f)).unwrap(); }
        std::fs::write(bundle.join("main.splash"),source).unwrap();
        let mut m=read(reference.join("manifest.json"));
        m["integrity"]=json!({"bundle_blake3":""});
        std::fs::write(bundle.join("manifest.json"),m.to_string()).unwrap();
        m["integrity"]["bundle_blake3"]=json!(octosense_app_policy::digest_dir(&bundle).unwrap());
        std::fs::write(bundle.join("manifest.json"),m.to_string()).unwrap();
        let reg=script_tools::bind(&mut cx,"ripple",&bundle,&card).unwrap().unwrap();
        (cx,ui,card,reg,jail)
    }
    fn submit(args: Value, timeout: Duration) -> Result<(String,Replies),String> {
        let replies:Replies=Default::default();let out=replies.clone();
        script_tools::submit("ripple","ripple.context.read",args,"device","protocol-harness",timeout,Box::new(move|r|out.lock().unwrap_or_else(|e|e.into_inner()).push(r))).map(|t|(t,replies))
    }
    fn invoke(cx:&mut Cx,card:&SplashRef,name:LiveId,args:&[&str]) {
        assert!(card.call_script_fn_with_strings(cx,name,args),"fixture function failed");
        makepad_platform::makepad_script_std::handle_script_tasks(cx);
    }
    fn pump(cx:&mut Cx,card:&SplashRef) {
        script_tools::pump(cx,"ripple",card);
        makepad_platform::makepad_script_std::handle_script_tasks(cx);
    }
    #[test]
    fn ripple_original_handler_schema_duplicates_timeout_cancel_and_reopen() {
        let bundle=root().join("phase1/probe-quota/bundle");
        let source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
        let (mut cx,_root,card,reg,jail)=fixture("original-protocol-jail",&source,&bundle);
        let schedule="ripple-test-v1|1791634960|1791638560|31.23|121.47|1";
        std::fs::write(jail.join("schedule.txt"),schedule).unwrap();
        let mut rejected=vec![];
        for args in [json!({"unexpected":1}),json!([]),json!("bad"),json!({"start":"invented"})] {
            let err=submit(args.clone(),Duration::from_secs(60)).err().unwrap();
            assert!(err.contains("invalid_arguments"));
            rejected.push(json!({"arguments":args,"error":err,"splash_executed":false}));
        }
        let (a,ra)=submit(json!({}),Duration::from_secs(60)).unwrap();
        let (b,rb)=submit(json!({}),Duration::from_secs(60)).unwrap();
        assert_ne!(a,b);
        pump(&mut cx,&card);
        for replies in [&ra,&rb] {
            assert_eq!(replies.lock().unwrap().len(),1);
            assert_eq!(replies.lock().unwrap()[0].as_ref().unwrap()["events"][0]["start"],1791634960);
        }
        let audit=std::fs::read_to_string(jail.join("phase1-tool-audit.log")).unwrap();
        invoke(&mut cx,&card,id!(app_tool),&["ripple.context.read",&a]);
        assert_eq!(std::fs::read_to_string(jail.join("phase1-tool-audit.log")).unwrap(),audit);
        assert_eq!(ra.lock().unwrap().len(),1);
        let (expired,re)=submit(json!({}),Duration::from_millis(2)).unwrap();
        std::thread::sleep(Duration::from_millis(8));
        pump(&mut cx,&card);
        assert!(re.lock().unwrap()[0].as_ref().unwrap_err().contains("timeout"));
        let (cancelled,rc)=submit(json!({}),Duration::from_secs(60)).unwrap();
        script_tools::cancel(&cancelled);
        pump(&mut cx,&card);
        invoke(&mut cx,&card,id!(app_tool),&["ripple.context.read",&cancelled]);
        assert_eq!(rc.lock().unwrap().len(),1);
        assert!(rc.lock().unwrap()[0].as_ref().unwrap_err().contains("cancelled"));
        let (closed,rl)=submit(json!({}),Duration::from_secs(60)).unwrap();
        drop(reg);
        invoke(&mut cx,&card,id!(app_tool),&["ripple.context.read",&closed]);
        assert_eq!(rl.lock().unwrap().len(),1);
        assert!(rl.lock().unwrap()[0].as_ref().unwrap_err().contains("app_not_running"));
        assert_eq!(std::fs::read_to_string(jail.join("schedule.txt")).unwrap(),schedule);
        let (mut cx2,_root2,card2,reg2,jail2)=fixture("reopened-protocol-jail",&source,&bundle);
        std::fs::write(jail2.join("schedule.txt"),schedule).unwrap();
        let (fresh,rf)=submit(json!({}),Duration::from_secs(60)).unwrap();
        assert_ne!(fresh,closed);
        // An old heap cannot claim a new generation's call token.
        invoke(&mut cx,&card,id!(app_tool),&["ripple.context.read",&fresh]);
        assert!(rf.lock().unwrap().is_empty());
        pump(&mut cx2,&card2);
        assert_eq!(rf.lock().unwrap()[0].as_ref().unwrap()["events"][0]["revision"],1);
        write("ripple-host-protocol-injection.json",&json!({"classification":"HOST_PROTOCOL_INJECTION","model_used":false,"schema_rejections":rejected,"duplicate_request_tokens":[a,b],"duplicate_completion_ignored":true,"timeout_token":expired,"timeout":re.lock().unwrap().clone(),"cancelled_token":cancelled,"cancel":rc.lock().unwrap().clone(),"closed_token":closed,"late_after_close":rl.lock().unwrap().clone(),"reopened_token":fresh,"old_heap_cannot_complete_new_call":true,"schedule_unchanged":true,"actual_returns":[ra.lock().unwrap().clone(),rb.lock().unwrap().clone(),rf.lock().unwrap().clone()]}));
        drop(reg2);
    }
    #[test]
    fn authoritative_time_and_model_errors_on_actual_splash_vm() {
        let bundle=root().join("phase1/probe-authority-timely/bundle");
        let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
        source.push_str(r#"
          fn fixture_clock(epoch) { let t=epoch.to_f64(); fs.write("clock.json",{utc:clock_stamp(t,0) utc8:clock_stamp(t,28800)}.to_json()) }
          fn fixture_guard(gen,text) { fs.write("guard.txt",validate_model_read(gen.to_f64(),text)) }
        "#);
        let (mut cx,_root,card,reg,jail)=fixture("authority-protocol-jail",&source,&bundle);
        let vectors=read(evidence().join("time-vectors-input.json"));
        let mut results=vec![];
        for v in vectors.as_array().unwrap() {
            let epoch=v["epoch"].to_string();
            invoke(&mut cx,&card,id!(fixture_clock),&[&epoch]);
            let actual=read(jail.join("clock.json"));
            assert_eq!(actual["utc"],v["utc"],"epoch {epoch}");
            assert_eq!(actual["utc8"],v["utc8"],"epoch {epoch}");
            results.push(json!({"epoch":v["epoch"],"actual":actual,"matched_independent_python_datetime":true}));
        }
        let schedule="ripple-test-v1|1791634960|1791638560|31.23|121.47|1";
        std::fs::write(jail.join("schedule.txt"),schedule).unwrap();
        invoke(&mut cx,&card,id!(begin_task),&["fixture-task"]);
        let (_,rr)=submit(json!({"task_id":"fixture-task"}),Duration::from_secs(60)).unwrap();
        pump(&mut cx,&card);
        let result=rr.lock().unwrap()[0].as_ref().unwrap().clone();
        let mut valid=json!({"task_id":"fixture-task","read_token":result["read_token"],"event_id":result["events"][0]["event_id"],"revision":1});
        invoke(&mut cx,&card,id!(fixture_guard),&["1",&valid.to_string()]);
        assert!(std::fs::read_to_string(jail.join("guard.txt")).unwrap().starts_with("ACCEPTED"));
        let mut rejected=vec![];
        for wrong in ["2026-10-09T11:01:46Z".to_string(),"garbage".to_string(),"[]".to_string(),"42".to_string()] {
            invoke(&mut cx,&card,id!(fixture_guard),&["1",&wrong]);
            let verdict=std::fs::read_to_string(jail.join("guard.txt")).unwrap();
            assert!(verdict.starts_with("REJECTED"));
            rejected.push(json!({"model_fixture":wrong,"verdict":verdict}));
        }
        valid["start_utc"]=json!("2026-10-09T11:01:46Z");
        invoke(&mut cx,&card,id!(fixture_guard),&["1",&valid.to_string()]);
        let wrong_date=std::fs::read_to_string(jail.join("guard.txt")).unwrap();
        assert!(wrong_date.contains("unexpected model field"));
        valid.as_object_mut().unwrap().remove("start_utc");
        valid["event_id"]=json!("invented-id");
        invoke(&mut cx,&card,id!(fixture_guard),&["1",&valid.to_string()]);
        assert!(std::fs::read_to_string(jail.join("guard.txt")).unwrap().contains("invented"));
        std::fs::write(jail.join("schedule.txt"),schedule.replace("|1","|2")).unwrap();
        invoke(&mut cx,&card,id!(fixture_guard),&["1",&valid.to_string()]);
        assert!(std::fs::read_to_string(jail.join("guard.txt")).unwrap().contains("schedule changed"));
        invoke(&mut cx,&card,id!(abandon_task),&["CANCELLED FIXTURE"]);
        invoke(&mut cx,&card,id!(fixture_guard),&["1",&valid.to_string()]);
        assert!(std::fs::read_to_string(jail.join("guard.txt")).unwrap().starts_with("DISCARDED"));
        assert!(!jail.join("authority-turn.json").exists());
        write("time-and-model-guard-fixtures.json",&json!({"classification":"DETERMINISTIC_FIXTURE_ON_REAL_SPLASH_VM","model_used":false,"time_vectors":results,"actual_read":result,"invalid_model_outputs":rejected,"wrong_model_date_verdict":wrong_date,"changed_revision_rejected":true,"cancelled_generation_discarded":true,"no_model_time_rendering":true,"no_executable_proposal_written":true}));
        drop(reg);
    }
    #[test]
    fn actual_readonly_slots_abi_and_independent_validation() {
        let bundle=root().join("phase2/readonly-prep/bundle");
        let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
        source.push_str(r#"
          fn fixture_validate(search,id,now) { fs.write("validated.json",{candidate:validate_candidate(search,id,now.to_f64())}.to_json()) }
        "#);
        let (mut cx,_root,card,reg,jail)=fixture("slots-protocol-jail",&source,&bundle);
        let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
        let base=(now/3600+1)*3600;
        let schedule=format!("ripple-test-v1|{}|{}|31.23|121.47|7",base+14400,base+18000);
        std::fs::write(jail.join("schedule.txt"),&schedule).unwrap();
        let hours:Vec<Value>=(0..9).map(|i| json!({"start":base-3600+i*3600,"end":base+i*3600,"code":if i==2 {61}else{0},"rain":if i==2 {2}else{0},"chance":if i==2 {80}else{0}})).collect();
        let mut weather=json!({"source":"FIXTURE","provider":"Open-Meteo","timezone":"GMT","utc_offset_seconds":0,"request_lat":31.23,"request_lon":121.47,"fetched_at":now-60,"revision":"fixture-w1","hours":hours});
        std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();
        invoke(&mut cx,&card,id!(begin_task),&["slots-task"]);
        let (_,rr)=submit(json!({"task_id":"slots-task"}),Duration::from_secs(60)).unwrap();pump(&mut cx,&card);
        let context=rr.lock().unwrap()[0].as_ref().unwrap().clone();
        let mut args=json!({"task_id":"slots-task","read_token":context["read_token"],"min_start":base,"max_end":base+21600,"max_candidates":3});
        let search=|args:Value,cx:&mut Cx,card:&SplashRef| -> Result<Value,String> {
            let replies:Replies=Default::default();let out=replies.clone();
            script_tools::submit("ripple","ripple.slots.search",args,"device","protocol-harness",Duration::from_secs(60),Box::new(move|r|out.lock().unwrap_or_else(|e|e.into_inner()).push(r)))?;
            pump(cx,card);let r=replies.lock().unwrap()[0].clone();r
        };
        let first=search(args.clone(),&mut cx,&card).unwrap();
        assert_eq!(first["weather_source"],"FIXTURE");
        assert_eq!(first["candidates"].as_array().unwrap().len(),3);
        assert_eq!(first["candidates"][0]["start"],base);
        assert_eq!(first["candidates"][1]["start"],base+7200);
        let search_id=first["search_id"].as_str().unwrap();let cid=first["candidates"][0]["candidate_id"].as_str().unwrap();
        invoke(&mut cx,&card,id!(fixture_validate),&[search_id,cid,&now.to_string()]);
        assert_eq!(read(jail.join("validated.json"))["candidate"]["start"],base);
        weather["hours"][0]["chance"]=json!(1);
        std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();
        invoke(&mut cx,&card,id!(fixture_validate),&[search_id,cid,&now.to_string()]);
        assert!(read(jail.join("validated.json"))["candidate"].is_null());
        weather["hours"][0]["chance"]=json!(0);
        std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();
        invoke(&mut cx,&card,id!(fixture_validate),&[search_id,"invented-candidate",&now.to_string()]);
        assert!(read(jail.join("validated.json"))["candidate"].is_null());
        args["min_start"]=json!(base+10800);let replanned=search(args.clone(),&mut cx,&card).unwrap();
        assert_eq!(replanned["candidates"][0]["start"],base+10800);
        invoke(&mut cx,&card,id!(fixture_validate),&[search_id,cid,&now.to_string()]);
        assert!(read(jail.join("validated.json"))["candidate"].is_null());
        let mut bad=args.clone();bad["max_candidates"]=json!(4);assert!(search(bad,&mut cx,&card).unwrap_err().contains("invalid_arguments"));
        bad=args.clone();bad["task_id"]=json!("stale-task");assert!(search(bad,&mut cx,&card).is_err());
        bad=args.clone();bad["min_start"]=json!(now-1);assert!(search(bad,&mut cx,&card).is_err());
        weather["fetched_at"]=json!(now-601);std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();assert!(search(args.clone(),&mut cx,&card).is_err());
        weather["fetched_at"]=json!(now-60);weather["request_lat"]=json!(32.0);std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();assert!(search(args.clone(),&mut cx,&card).is_err());
        weather["request_lat"]=json!(31.23);weather["hours"][2]["end"]=json!(base+10);std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();assert!(search(args.clone(),&mut cx,&card).is_err());
        weather["hours"]=json!((0..9).map(|i|json!({"start":base-3600+i*3600,"end":base+i*3600,"code":61,"rain":2,"chance":80})).collect::<Vec<_>>());
        std::fs::write(jail.join("weather.json"),weather.to_string()).unwrap();let none=search(args,&mut cx,&card).unwrap();assert_eq!(none["candidates"].as_array().unwrap().len(),0);
        assert_eq!(std::fs::read_to_string(jail.join("schedule.txt")).unwrap(),schedule);
        write("readonly-slots-actual-abi.json",&json!({"classification":"HOST_PROTOCOL_INJECTION_WITH_FIXTURE_WEATHER","real_model_used":false,"tools":["ripple.context.read","ripple.slots.search"],"actual_context":context,"actual_search":first,"new_constraints_search":replanned,"no_feasible_candidate":none,"schema_rejection":true,"stale_task_rejected":true,"past_time_rejected":true,"stale_weather_rejected":true,"wrong_coordinates_rejected":true,"incomplete_weather_rejected":true,"invented_candidate_rejected":true,"weather_content_change_without_revision_change_rejected":true,"previous_search_invalidated":true,"schedule_unchanged":true,"approval_state_machine_connected":false}));
        drop(reg);
    }
}
