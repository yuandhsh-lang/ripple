// Stage 1 uses the same pinned VM and real AppTools ABI as the core tests.
// HTTP bodies/weather below are explicit fixtures, never live-network evidence.
#[test]
fn stage1_city_window_compatibility_and_approval() {
    let bundle=root().join("stage1/bundle");
    let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
    source.push_str(r#"
      fn s1_geo(query,code,body){ ui.city_input.set_text(query) city_query=query city_results=geocode_results(code.to_f64(),body) }
      fn s1_select(index){ choose_city(city_results[index.to_f64()].id) }
      fn s1_save(start,left,right,duration){ let before=schedule_fingerprint() let pending=status=="AWAITING_APPROVAL" ui.title_input.set_text("Synthetic Stage 1 park walk") ui.start_input.set_text(start) ui.duration.set_text(duration) ui.available_start.set_text(left) ui.available_end.set_text(right) save_activity() finish_save(before,pending) }
      fn s1_clock(epoch){ fs.write("clock.json",{stamp:local_date(epoch.to_f64())+" "+local_clock(epoch.to_f64())}.to_json()) }
      fn s1_report(){ fs.write("stage1.json",{status:status message:message city_message:city_message city:selected_city results:city_results dirty:dirty event:read_event() proposal:proposal search:last_search verified:verified manual:manual_location window_start:ui.available_start.text() window_end:ui.available_end.text()}.to_json()) }
      fn s1_preview(){ workflow_started=time_now() event=read_event() planning_mode="user" preview_candidates() }
      fn s1_search(){ preview_search(task_generation,input_generation) }
      fn s1_first(){ choose_candidate(last_search.candidates[0].candidate_id) }
      fn s1_reset(){ busy=false loading=false proposal=nil status="READY" }
      fn s1_draft(){ draft_changed() }
      fn s1_pending_save(){ save_activity() }
      fn s1_finish_save(){ finish_save(read_json("execution.json").before,false) }
      fn s1_validate(text){ let accepted=try { valid_event(text.parse_json()) } catch { false } fs.write("valid.json",{valid:accepted}.to_json()) }
      fn s1_tamper(){ let next=proposal.expected.parse_json() next.availability.max_end=next.availability.max_end+1800 proposal.expected=record(next) }
      fn s1_timeout(){ busy=true status="CHECKING" preview_timeout(task_generation) }
      fn s1_agent_begin(){ workflow_started=time_now() begin_task("schema-city-tool") move("ANALYZING","Explicit protocol fixture") }
    "#);
    let (mut cx,_ui,card,reg,jail)=fixture("stage1-jail",&source,&bundle);
    let report=|cx:&mut Cx|->Value{invoke(cx,&card,id!(s1_report),&[]);read(jail.join("stage1.json"))};
    let preview=|cx:&mut Cx|{invoke(cx,&card,id!(s1_preview),&[]);invoke(cx,&card,id!(s1_search),&[]);};
    let city=|id:u64,name:&str,zone:&str|json!({"id":id,"name":name,"country":"中国","country_code":"CN","admin1":"广东","admin2":"测试地区","latitude":22.54554,"longitude":114.0683,"timezone":zone});
    let good=city(1795565,"深圳","Asia/Shanghai");
    let body=json!({"results":[good.clone(),city(8420705,"深圳","Asia/Shanghai")]});
    invoke(&mut cx,&card,id!(s1_geo),&["深圳","200",&body.to_string()]);
    let ambiguous=report(&mut cx);assert!(ambiguous["city"].is_null());assert_eq!(ambiguous["results"].as_array().unwrap().len(),2);
    invoke(&mut cx,&card,id!(s1_select),&["1"]);assert_eq!(report(&mut cx)["city"]["id"],8420705);
    let mut bad=good.clone();bad["latitude"]=json!(91);
    let mut missing=good.clone();missing.as_object_mut().unwrap().remove("timezone");
    let failures=vec![("empty","200",json!({}).to_string()),("HTTP","503",body.to_string()),("malformed","200","{bad".into()),("missing timezone","200",json!({"results":[missing]}).to_string()),("illegal coordinate","200",json!({"results":[bad]}).to_string())];
    let mut cases=Vec::new();
    for (label,code,body) in failures {
        invoke(&mut cx,&card,id!(s1_geo),&["test",code,&body]);let r=report(&mut cx);
        assert_eq!(r["results"],json!([]));cases.push(json!({"case":label,"result":r["city_message"]}));
    }
    invoke(&mut cx,&card,id!(s1_geo),&["New York","200",&json!({"results":[city(1,"New York","America/New_York")]}).to_string()]);
    invoke(&mut cx,&card,id!(s1_select),&["0"]);assert!(report(&mut cx)["city"].is_null());
    invoke(&mut cx,&card,id!(s1_geo),&["深圳","200",&json!({"results":[good.clone()]}).to_string()]);invoke(&mut cx,&card,id!(s1_select),&["0"]);
    let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
    let day=((now+28800)/86400+1)*86400-28800;
    invoke(&mut cx,&card,id!(s1_clock),&[&(day+15*3600).to_string()]);let start=read(jail.join("clock.json"))["stamp"].as_str().unwrap().to_string();
    let save=|left:&str,right:&str,duration:&str,cx:&mut Cx|{invoke(cx,&card,id!(s1_reset),&[]);invoke(cx,&card,id!(s1_save),&[&start,left,right,duration]);};
    save("09:00","14:00","60",&mut cx);
    let saved=read(jail.join("schedule.txt"));assert_eq!(saved["schema"],3);assert_eq!(saved["availability"]["min_start"],day+9*3600);assert_eq!(saved["availability"]["max_end"],day+14*3600);assert_eq!(saved["timezone"],"Asia/Shanghai");assert_eq!(saved["location"]["name"],"深圳");
    invoke(&mut cx,&card,id!(boot),&[]);let reboot=report(&mut cx);assert_eq!(reboot["event"],saved);assert_eq!(reboot["window_start"],"09:00");assert_eq!(reboot["window_end"],"14:00");
    for (left,right,duration) in [("09:00","09:30","60"),("14:00","09:00","60"),("09:00","09:00","60"),("09:00","","60"),("23:00","01:00","60"),("09:00","14:00","0"),("25:00","26:00","60")] {
        save(left,right,duration,&mut cx);let r=report(&mut cx);assert_eq!(r["status"],"FAILED","{left}/{right}/{duration}: {r}");assert_eq!(read(jail.join("schedule.txt")),saved);
    }
    for bad_start in [format!("{} 23:30",&start[..10]),"2000-01-01 15:00".into()] {
        invoke(&mut cx,&card,id!(s1_save),&[&bad_start,"","","60"]);assert_eq!(report(&mut cx)["status"],"FAILED");assert_eq!(read(jail.join("schedule.txt")),saved);
    }
    let weather=|wet_all:bool|json!({"source":"FIXTURE","provider":"Open-Meteo","timezone":"GMT","utc_offset_seconds":0,"request_lat":22.54554,"request_lon":114.0683,"fetched_at":now,"revision":"explicit-stage1-fixture","hours":(0..24).map(|i|json!({"start":day+i*3600,"end":day+(i+1)*3600,"code":if wet_all||i==15 {61}else{0},"rain":if wet_all||i==15 {2}else{0},"chance":if wet_all||i==15 {80}else{0}})).collect::<Vec<_>>()});
    let install_weather=|w:&Value|std::fs::write(jail.join("weather.json"),w.to_string()).unwrap();
    install_weather(&weather(false));save("09:00","14:00","60",&mut cx);
    invoke(&mut cx,&card,id!(s1_agent_begin),&[]);
    let replies:Replies=Default::default();let out=replies.clone();
    script_tools::submit("ripple","ripple.context.read",json!({"task_id":"schema-city-tool"}),"device","stage1-city-schema",Duration::from_secs(60),Box::new(move|r|out.lock().unwrap().push(r))).unwrap();pump(&mut cx,&card);
    let city_context=replies.lock().unwrap()[0].clone().expect("actual city output must satisfy AppTools schema");
    assert_eq!(city_context["events"][0]["location"]["id"],1795565);assert_eq!(city_context["events"][0]["availability"],saved["availability"]);
    preview(&mut cx);let preview_result=report(&mut cx);assert_eq!(preview_result["status"],"CANDIDATES");
    assert_eq!(preview_result["search"]["candidates"][0]["start"],day+9*3600);
    for c in preview_result["search"]["candidates"].as_array().unwrap(){assert!(c["end"].as_u64().unwrap()<=day+14*3600);assert_eq!(c["checks"]["availability_declared"],true);}
    // The original 15:00 activity lies outside 09:00–14:00; legal moves still exist.
    save("13:00","14:00","60",&mut cx);preview(&mut cx);let end_boundary=report(&mut cx);assert_eq!(end_boundary["search"]["candidates"].as_array().unwrap().len(),1);assert_eq!(end_boundary["search"]["candidates"][0]["end"],day+14*3600);
    save("09:10","10:10","60",&mut cx);preview(&mut cx);assert_eq!(report(&mut cx)["search"]["candidates"][0]["start"],day+9*3600+600);
    // Empty declaration permits save and risk reading, but never an actionable move.
    save("","","60",&mut cx);preview(&mut cx);assert_eq!(report(&mut cx)["status"],"NO_CANDIDATE");assert!(read(jail.join("schedule.txt"))["availability"].is_null());
    save("09:00","14:00","60",&mut cx);install_weather(&weather(true));preview(&mut cx);assert_eq!(report(&mut cx)["status"],"NO_CANDIDATE");
    let mut incomplete=weather(false);incomplete["hours"].as_array_mut().unwrap().remove(10);install_weather(&incomplete);preview(&mut cx);assert_eq!(report(&mut cx)["status"],"FAILED");
    let mut limited=weather(false);limited["hours"].as_array_mut().unwrap().retain(|x|x["start"].as_u64().unwrap()>=day+14*3600);install_weather(&limited);preview(&mut cx);assert_eq!(report(&mut cx)["status"],"NO_CANDIDATE");
    install_weather(&weather(false));preview(&mut cx);invoke(&mut cx,&card,id!(s1_first),&[]);assert_eq!(report(&mut cx)["status"],"AWAITING_APPROVAL");
    let unapproved=read(jail.join("schedule.txt"));invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),unapproved);
    // Native edits invalidate a pending choice even before Save; no old consent.
    invoke(&mut cx,&card,id!(s1_draft),&[]);invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),unapproved);assert!(report(&mut cx)["proposal"].is_null());
    save("09:00","14:00","60",&mut cx);preview(&mut cx);invoke(&mut cx,&card,id!(s1_first),&[]);
    invoke(&mut cx,&card,id!(s1_save),&[&start,"13:00","14:00","60"]);assert_eq!(report(&mut cx)["status"],"STALE");let changed_window=read(jail.join("schedule.txt"));
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),changed_window);
    save("09:00","14:00","60",&mut cx);preview(&mut cx);invoke(&mut cx,&card,id!(s1_first),&[]);
    invoke(&mut cx,&card,id!(s1_geo),&["深圳","200",&body.to_string()]);invoke(&mut cx,&card,id!(s1_select),&["1"]);assert_eq!(report(&mut cx)["status"],"STALE");assert!(report(&mut cx)["proposal"].is_null());
    invoke(&mut cx,&card,id!(s1_save),&[&start,"09:00","14:00","60"]);let changed_city=read(jail.join("schedule.txt"));assert_eq!(changed_city["location"]["id"],8420705);
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),changed_city);
    invoke(&mut cx,&card,id!(s1_geo),&["深圳","200",&json!({"results":[good.clone()]}).to_string()]);invoke(&mut cx,&card,id!(s1_select),&["0"]);
    save("09:00","14:00","60",&mut cx);preview(&mut cx);invoke(&mut cx,&card,id!(s1_first),&[]);invoke(&mut cx,&card,id!(s1_tamper),&[]);let intact=read(jail.join("schedule.txt"));
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(report(&mut cx)["status"],"STALE");assert_eq!(read(jail.join("schedule.txt")),intact);
    preview(&mut cx);invoke(&mut cx,&card,id!(s1_timeout),&[]);assert_eq!(report(&mut cx)["status"],"FAILED");invoke(&mut cx,&card,id!(s1_search),&[]);assert_eq!(read(jail.join("schedule.txt")),intact);assert!(report(&mut cx)["proposal"].is_null());
    save("09:00","14:00","60",&mut cx);preview(&mut cx);invoke(&mut cx,&card,id!(s1_first),&[]);
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);invoke(&mut cx,&card,id!(finish_verify),&[]);let completed=report(&mut cx);assert_eq!(completed["status"],"COMPLETED");assert_eq!(completed["verified"],true);
    let after=read(jail.join("schedule.txt"));assert_eq!(after["location"],saved["location"]);assert_eq!(after["availability"],saved["availability"]);assert_eq!(after["start"],day+9*3600);
    invoke(&mut cx,&card,id!(confirm),&[]);invoke(&mut cx,&card,id!(execute),&[]);assert_eq!(read(jail.join("schedule.txt")),after);
    // Backward-compatible reading is byte-preserving; explicit save is the only migration.
    let legacy=json!({"schema":2,"event_id":"legacy-id","title":"Legacy coordinates only","start":day+15*3600,"end":day+16*3600,"lat":22.54554,"lon":114.0683,"revision":7,"data_source":"ripple-local-activity"});
    let raw=legacy.to_string();std::fs::write(jail.join("schedule.txt"),&raw).unwrap();
    // A matching historical SAVE receipt has no schema 3 assumptions.
    std::fs::write(jail.join("execution.json"),json!({"kind":"SAVE","before":"EMPTY","expected":raw}).to_string()).unwrap();invoke(&mut cx,&card,id!(boot),&[]);let old=report(&mut cx);assert_eq!(old["manual"],true);assert!(old["city"].is_null());assert_eq!(old["window_start"],"");assert_eq!(std::fs::read_to_string(jail.join("schedule.txt")).unwrap(),raw);
    preview(&mut cx);assert_eq!(report(&mut cx)["status"],"NO_CANDIDATE");
    save("","","60",&mut cx);let migrated=read(jail.join("schedule.txt"));assert_eq!(migrated["schema"],3);assert_eq!(migrated["event_id"],"legacy-id");assert_eq!(migrated["revision"],8);assert!(migrated["location"].is_null());assert!(migrated["availability"].is_null());
    invoke(&mut cx,&card,id!(s1_pending_save),&[]);invoke(&mut cx,&card,id!(s1_draft),&[]);invoke(&mut cx,&card,id!(s1_finish_save),&[]);
    assert_eq!(report(&mut cx)["dirty"],true,"an edit during save must remain unsaved");
    let saved_before_edit=read(jail.join("schedule.txt"));invoke(&mut cx,&card,id!(analyze),&[]);assert_eq!(read(jail.join("schedule.txt")),saved_before_edit);
    for field in ["timezone","availability","location"] {
        let mut corrupt=migrated.clone();corrupt[field]=json!("bad");invoke(&mut cx,&card,id!(s1_validate),&[&corrupt.to_string()]);assert_eq!(read(jail.join("valid.json"))["valid"],false);
    }
    assert!(!std::fs::read_to_string(jail.join("agent-audit.log")).unwrap().contains("Synthetic Stage 1 park walk"));
    write("stage1-city-window.json",&json!({"classification":"ACTUAL_PINNED_SDK_VM_EXPLICIT_FIXTURE_CITY_WEATHER_NO_MODEL","ambiguous_without_autoselect":ambiguous,"geocode_failures":cases,"saved":saved,"reboot":reboot,"preview":preview_result,"exact_end_boundary":end_boundary,"completed":completed,"legacy_read":old,"explicit_migration":migrated,"unsupported_timezone_rejected":true,"incomplete_weather_rejected":true,"no_unapproved_write":true,"duplicate_execution_no_write":true,"ordinary_log_omits_title":true}));
    drop(reg);
}
