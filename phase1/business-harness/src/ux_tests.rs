// New UX actions run against the existing VM, validator and sole write/read-back path.
// Explicit draft fixtures here are not real model evidence.
#[test]
fn reviewed_draft_save_and_edit_guards() {
    let bundle=root().join("stage1/bundle");
    let mut source=std::fs::read_to_string(bundle.join("main.splash")).unwrap();
    source.push_str(r#"
      fn ux_seed(text){ busy=false loading=false review_index=-2 review_edit=nil interpret_text="EXPLICIT UX FIXTURE" let d=validate_draft(text.parse_json()) interpretation_draft={data:d fingerprint:schedule_fingerprint() inputs:input_generation} move("DRAFT_REVIEW","Fixture draft, not a real model") }
      fn ux_validate(text){ fs.write("valid-draft.json",{accepted:validate_draft(text.parse_json()) != nil}.to_json()) }
      fn ux_city(text){ selected_city=text.parse_json() }
      fn ux_report(){ fs.write("ux.json",{status:status message:review_message draft:interpretation_draft dirty:dirty busy:busy edit:review_edit}.to_json()) }
      fn ux_edit(index){ edit_review(index.to_f64()) }
      fn ux_replace_edit(text){ review_edit=text.parse_json() }
      fn ux_finish(before){ finish_save(before,false) }
      fn ux_busy(){ busy=true }
      fn ux_idle(){ busy=false }
      fn ux_clock(epoch){ fs.write("clock.json",{text:local_date(epoch.to_f64())+" "+local_clock(epoch.to_f64())}.to_json()) }
    "#);
    let (mut cx,_ui,card,reg,jail)=fixture("ux-draft",&source,&bundle);
    let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();let day=((now+28800)/86400+1)*86400-28800;
    invoke(&mut cx,&card,id!(ux_clock),&[&(day+15*3600).to_string()]);
    let mut draft=json!({"title":"骑行","city_query":"北京","start_text":read(jail.join("clock.json"))["text"],"duration_minutes":60,"window_start":"","window_end":"","primary_movable":true,"priority":3,"preference":"morning","plans":[]});
    let city=json!({"id":1816670,"name":"北京","country":"中国","country_code":"CN","admin1":"北京市","admin2":"北京市","lat":39.9075,"lon":116.39723,"timezone":"Asia/Shanghai","source":"Open-Meteo / GeoNames"});
    let report=|cx:&mut Cx|{invoke(cx,&card,id!(ux_report),&[]);read(jail.join("ux.json"))};
    invoke(&mut cx,&card,id!(ux_seed),&[&draft.to_string()]);
    assert_eq!(report(&mut cx)["status"],"DRAFT_REVIEW");assert!(!jail.join("schedule.txt").exists());
    invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert!(!jail.join("schedule.txt").exists(),"city needs human confirmation");
    invoke(&mut cx,&card,id!(city_input_changed),&[]);assert_eq!(report(&mut cx)["status"],"DRAFT_REVIEW","city lookup must preserve the reviewed draft");assert!(report(&mut cx)["draft"].is_object());
    invoke(&mut cx,&card,id!(ux_city),&[&city.to_string()]);
    invoke(&mut cx,&card,id!(ux_edit),&["-1"]);let mut edit=report(&mut cx)["edit"].clone();
    edit["left"]=json!("09:00");edit["right"]=json!("09:30");
    invoke(&mut cx,&card,id!(ux_replace_edit),&[&edit.to_string()]);invoke(&mut cx,&card,id!(commit_review_edit),&[]);
    assert_eq!(report(&mut cx)["draft"]["data"]["fields"]["window_start"],"","invalid shorter window must not replace valid draft");
    invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert!(!jail.join("schedule.txt").exists(),"unfinished invalid edit blocks saving");
    edit["right"]=json!("10:00");edit["title"]=json!("北京骑行");
    invoke(&mut cx,&card,id!(ux_replace_edit),&[&edit.to_string()]);invoke(&mut cx,&card,id!(commit_review_edit),&[]);
    assert_eq!(report(&mut cx)["draft"]["data"]["fields"]["title"],"北京骑行");
    invoke(&mut cx,&card,id!(ux_busy),&[]);invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert!(!jail.join("schedule.txt").exists());invoke(&mut cx,&card,id!(ux_idle),&[]);
    invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);let saved=read(jail.join("schedule.txt"));
    assert_eq!(saved["start"],day+15*3600);assert_eq!(saved["availability"]["min_start"],day+9*3600,"original time and allowed reschedule window are distinct");assert_eq!(saved["planning"]["preference"],"morning");
    invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert_eq!(read(jail.join("schedule.txt")),saved,"repeat approval while saving cannot write twice");
    invoke(&mut cx,&card,id!(ux_finish),&["EMPTY"]);assert_eq!(report(&mut cx)["status"],"READY");
    invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert_eq!(read(jail.join("schedule.txt")),saved,"finished draft cannot be reused");
    draft["title"]=json!("北京骑行");draft["window_start"]=json!("09:00");draft["window_end"]=json!("10:00");
    let mut repeated_primary=draft.clone();
    invoke(&mut cx,&card,id!(ux_clock),&[&(day+16*3600).to_string()]);
    repeated_primary["plans"]=json!([{"id":saved["event_id"],"title":"骑行","city_query":"北京","start_text":draft["start_text"],"end_text":read(jail.join("clock.json"))["text"],"active":true,"movable":true,"outdoor":true,"priority":3,"window_start":"09:00","window_end":"10:00"}]);
    invoke(&mut cx,&card,id!(ux_validate),&[&repeated_primary.to_string()]);
    assert_eq!(read(jail.join("valid-draft.json"))["accepted"],false,"saved primary identity must be rejected during draft validation, not late during saving");
    assert_eq!(read(jail.join("schedule.txt")),saved);
    invoke(&mut cx,&card,id!(ux_clock),&[&(day+9*3600).to_string()]);draft["start_text"]=read(jail.join("clock.json"))["text"].clone();
    invoke(&mut cx,&card,id!(ux_seed),&[&draft.to_string()]);invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert_eq!(read(jail.join("schedule.txt")),saved,"AI interpretation cannot replace a saved time through the draft save shortcut");
    let mut concurrent=saved.clone();concurrent["revision"]=json!(2);std::fs::write(jail.join("schedule.txt"),concurrent.to_string()).unwrap();
    invoke(&mut cx,&card,id!(save_reviewed_draft),&[]);assert_eq!(report(&mut cx)["status"],"STALE");assert_eq!(read(jail.join("schedule.txt")),concurrent);
    write("ux-draft-safety.json",&json!({"classification":"ACTUAL_VM_EXPLICIT_DRAFT_FIXTURE","saved":saved,"receipt":read(jail.join("execution.json")),"repeated_primary_rejected_before_review":true,"city_confirmation_required":true,"invalid_edit_blocked":true,"busy_and_duplicate_blocked":true,"soft_preference_distinct_from_window":true,"existing_time_change_needs_separate_path":true,"stale_draft_blocked":true}));
    drop(reg);
}
