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
    fn read(p: impl AsRef<Path>) -> Value { serde_json::from_slice(&std::fs::read(p.as_ref()).unwrap_or_else(|e|panic!("read {}: {e}",p.as_ref().display()))).unwrap() }
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
    fn invoke(cx:&mut Cx,card:&SplashRef,name:LiveId,args:&[&str]) {
        assert!(card.call_script_fn_with_strings(cx,name,args),"fixture function failed");
        makepad_platform::makepad_script_std::handle_script_tasks(cx);
    }
    fn pump(cx:&mut Cx,card:&SplashRef) {
        script_tools::pump(cx,"ripple",card);
        makepad_platform::makepad_script_std::handle_script_tasks(cx);
    }

    #[test]
    fn business_abi_approval_readback_and_guards() {
        let bundle=root().join("stage1/bundle");
        let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
        source.push_str(r#"
          fn fixture_inputs(title,start,duration,lat,lon){ ui.title_input.set_text(title) ui.start_input.set_text(start) ui.duration.set_text(duration) ui.latitude.set_text(lat) ui.longitude.set_text(lon) save_activity() }
          fn fixture_begin(id){ workflow_started=time_now() begin_task(id) }
          fn fixture_finish(text){ finish_model(task_generation,text) }
          fn fixture_report(){ fs.write("report.json",{status:status message:message busy:busy proposal:proposal verified:verified replan_count:replan_count}.to_json()) }
          fn fixture_clock(epoch){ fs.write("clock.json",{utc:clock_stamp(epoch.to_f64(),0) utc8:clock_stamp(epoch.to_f64(),28800)}.to_json()) }
          fn fixture_parse(text){ fs.write("parsed.json",{epoch:parse_start(text)}.to_json()) }
          fn fixture_expire(){ proposal.created=time_now()-601 proposal.expires_at=time_now()-1 }
          fn fixture_replan_limit(mode){ busy=false loading=false status="STALE" proposal=nil replan_count=0 workflow_started=time_now() if mode=="count" { replan_count=1 } else { workflow_started=time_now()-1201 } replan() }
        "#);
        let (mut cx,_ui,card,reg,jail)=fixture("business-jail",&source,&bundle);
        let vectors=read(root().join("phase1/business-harness/time-vectors.json"));
        for v in vectors.as_array().unwrap() {
            invoke(&mut cx,&card,id!(fixture_clock),&[&v["epoch"].to_string()]);
            let actual=read(jail.join("clock.json"));
            assert_eq!(actual["utc"],v["utc"]);assert_eq!(actual["utc8"],v["utc8"]);
        }
        write("current-time-vectors.json",&json!({"classification":"CURRENT_SPLASH_VM_VS_INDEPENDENT_PYTHON_DATETIME_GOLDEN","count":vectors.as_array().unwrap().len(),"passed":true,"vectors":vectors}));
        let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
        let base=(now/3600+1)*3600;
        invoke(&mut cx,&card,id!(fixture_clock),&[&(base+14400).to_string()]);
        let stamp=read(jail.join("clock.json"))["utc8"].as_str().unwrap().replace('T'," ");
        let start=&stamp[..16];
        invoke(&mut cx,&card,id!(fixture_inputs),&["My outdoor walk",start,"120","31.23","121.47"]);
        let before=read(jail.join("schedule.txt"));assert_eq!(before["title"],"My outdoor walk");assert_eq!(before["start"],base+14400);assert_eq!(before["end"],base+21600);
        let id=before["event_id"].clone();assert!(!id.as_str().unwrap().is_empty());
        invoke(&mut cx,&card,id!(boot),&[]);invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"READY");
        for bad in ["2026-02-30 10:00","2026-13-01 10:00","2026-10-11 24:00","not a date"] {
            invoke(&mut cx,&card,id!(fixture_parse),&[bad]);assert!(read(jail.join("parsed.json"))["epoch"].is_null());
        }
        let hours:Vec<Value>=(0..60).map(|i|json!({"start":base-3600+i*3600,"end":base+i*3600,"code":if i==5 {61}else{0},"rain":if i==5 {2}else{0},"chance":if i==5 {80}else{0}})).collect();
        let mut w=json!({"source":"FIXTURE","provider":"Open-Meteo","timezone":"GMT","utc_offset_seconds":0,"request_lat":31.23,"request_lon":121.47,"fetched_at":now-5,"revision":"fixture-business-w1","hours":hours});
        std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();
        let call=|name:&str,args:Value,cx:&mut Cx|->Result<Value,String>{
            let replies:Replies=Default::default();let out=replies.clone();
            script_tools::submit("ripple",name,args,"device","business-protocol-harness",Duration::from_secs(60),Box::new(move|r|out.lock().unwrap().push(r)))?;
            pump(cx,&card);let answer=replies.lock().unwrap().get(0).cloned().expect("actual handler did not complete");answer
        };
        let plan=|label:&str,cx:&mut Cx|->(Value,Value,Value){
            invoke(cx,&card,id!(fixture_begin),&[label]);
            let context=call("ripple.context.read",json!({"task_id":label}),cx).unwrap();assert_eq!(context["impact"]["conflict"],true);
            let mut args=context["search_bounds"].clone();args["task_id"]=json!(label);args["read_token"]=context["read_token"].clone();
            let search=call("ripple.slots.search",args,cx).unwrap();
            let choice=json!({"task_id":label,"read_token":context["read_token"],"decision":"PROPOSE","search_id":search["search_id"],"candidate_id":search["candidates"][0]["candidate_id"]});
            (context,search,choice)
        };
        assert!(call("ripple.context.read",json!({"task_id":"x","invented":1}),&mut cx).unwrap_err().contains("invalid_arguments"));
        let (context,search,choice)=plan("business-decline",&mut cx);
        assert_eq!(search["candidates"][0]["end"].as_u64().unwrap()-search["candidates"][0]["start"].as_u64().unwrap(),7200);
        let mut invented=choice.clone();invented["candidate_id"]=json!("invented");invoke(&mut cx,&card,id!(fixture_finish),&[&invented.to_string()]);
        invoke(&mut cx,&card,id!(fixture_report),&[]);assert_ne!(read(jail.join("report.json"))["status"],"AWAITING_APPROVAL");assert_eq!(read(jail.join("schedule.txt")),before);
        let (_,_,declined)=plan("decline-valid",&mut cx);invoke(&mut cx,&card,id!(fixture_finish),&[&declined.to_string()]);
        invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"AWAITING_APPROVAL");
        invoke(&mut cx,&card,id!(decline),&[]);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),before);
        let (_,_,changed_choice)=plan("changed",&mut cx);invoke(&mut cx,&card,id!(fixture_finish),&[&changed_choice.to_string()]);
        invoke(&mut cx,&card,id!(fixture_inputs),&["Edited walk",start,"120","31.23","121.47"]);
        let changed=read(jail.join("schedule.txt"));assert_eq!(changed["event_id"],id);assert_eq!(changed["revision"],2);
        invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),changed);
        let (_,_,weather_choice)=plan("weather-changed",&mut cx);invoke(&mut cx,&card,id!(fixture_finish),&[&weather_choice.to_string()]);
        w["hours"][0]["chance"]=json!(1);std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();
        invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"STALE");assert_eq!(read(jail.join("schedule.txt")),changed);
        w["hours"][0]["chance"]=json!(0);std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();
        let (_,_,expired_choice)=plan("expired",&mut cx);invoke(&mut cx,&card,id!(fixture_finish),&[&expired_choice.to_string()]);
        w["fetched_at"]=json!(now-601);std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();
        invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),changed);
        w["fetched_at"]=json!(now-5);std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();
        let (_,_,aged_choice)=plan("aged-proposal",&mut cx);invoke(&mut cx,&card,id!(fixture_finish),&[&aged_choice.to_string()]);
        invoke(&mut cx,&card,id!(fixture_expire),&[]);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(fixture_report),&[]);
        assert_eq!(read(jail.join("report.json"))["status"],"STALE");assert_eq!(read(jail.join("schedule.txt")),changed);
        let (_,_,late)=plan("cancelled",&mut cx);invoke(&mut cx,&card,id!(abandon_task),&["Cancel fixture"]);invoke(&mut cx,&card,id!(fixture_finish),&[&late.to_string()]);assert_eq!(read(jail.join("schedule.txt")),changed);
        let (_,executed_search,approved)=plan("execute-valid",&mut cx);invoke(&mut cx,&card,id!(fixture_finish),&[&approved.to_string()]);
        invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);
        invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"VERIFYING");
        invoke(&mut cx,&card,id!(finish_verify),&[]);let after=read(jail.join("schedule.txt"));
        assert_eq!(after["event_id"],id);assert_eq!(after["revision"],3);assert_eq!(after["start"],executed_search["candidates"][0]["start"]);assert_eq!(after["title"],"Edited walk");
        invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),after);
        invoke(&mut cx,&card,id!(boot),&[]);invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"COMPLETED");assert_eq!(read(jail.join("report.json"))["verified"],true);
        // Real read after execution sees a dry activity; no fabricated model success.
        invoke(&mut cx,&card,id!(fixture_begin),&["dry"]);let dry=call("ripple.context.read",json!({"task_id":"dry"}),&mut cx).unwrap();assert_eq!(dry["impact"]["conflict"],false);
        let nochange=json!({"task_id":"dry","read_token":dry["read_token"],"decision":"NO_CHANGE","search_id":null,"candidate_id":null});invoke(&mut cx,&card,id!(fixture_finish),&[&nochange.to_string()]);invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"NO_CHANGE");
        // No-weather and no-candidate paths must never propose or modify.
        std::fs::remove_file(jail.join("weather.json")).unwrap();invoke(&mut cx,&card,id!(fixture_begin),&["missing-weather"]);assert!(call("ripple.context.read",json!({"task_id":"missing-weather"}),&mut cx).is_err());
        for h in w["hours"].as_array_mut().unwrap(){h["code"]=json!(61);h["rain"]=json!(2);h["chance"]=json!(80);}
        std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();invoke(&mut cx,&card,id!(fixture_begin),&["no-candidate"]);
        let nc=call("ripple.context.read",json!({"task_id":"no-candidate"}),&mut cx).unwrap();let mut args=nc["search_bounds"].clone();args["task_id"]=json!("no-candidate");args["read_token"]=nc["read_token"].clone();
        let none=call("ripple.slots.search",args,&mut cx).unwrap();assert_eq!(none["candidates"],json!([]));
        let ncchoice=json!({"task_id":"no-candidate","read_token":nc["read_token"],"decision":"NO_CANDIDATE","search_id":none["search_id"],"candidate_id":null});invoke(&mut cx,&card,id!(fixture_finish),&[&ncchoice.to_string()]);invoke(&mut cx,&card,id!(fixture_report),&[]);assert_eq!(read(jail.join("report.json"))["status"],"NO_CANDIDATE");assert_eq!(read(jail.join("schedule.txt")),after);
        for mode in ["count","expiry"] {
            invoke(&mut cx,&card,id!(fixture_replan_limit),&[mode]);invoke(&mut cx,&card,id!(fixture_report),&[]);
            assert_eq!(read(jail.join("report.json"))["status"],"FAILED");assert_eq!(read(jail.join("schedule.txt")),after);
        }
        write("business-abi-results.json",&json!({"classification":"ACTUAL_SDK_ABI_AND_SPLASH_VM_WITH_FIXTURE_WEATHER_AND_MODEL_REPLY","real_model_used":false,"created_activity":before,"context":context,"search":search,"executed_choice":approved,"independent_readback":after,"dry_context":dry,"no_candidate":none,"guards_verified":["invalid input date","invalid tool schema","invented candidate","decline no write","identity stable across edit","changed revision stale","weather content stale","expired weather","expired proposal unchanged weather","cancelled late choice","double approval","duplicate execution","boot readback","no change","no weather","no candidate","one replan limit","workflow expiry"]}));
        drop(reg);
    }
}
