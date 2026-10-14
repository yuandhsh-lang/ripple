// Explicit diagnostic only. No SDK edits, budget mutation, or relaxed assertions.
thread_local! {
    static INIT_MARKS: std::cell::RefCell<Vec<Value>> = const { std::cell::RefCell::new(Vec::new()) };
}
fn init_probe_module(vm: &mut ScriptVm) {
    let module = vm.new_module(id!(ripple_init_probe));
    vm.add_method(module, id_lut!(mark), script_args_def!(phase=NIL), |vm,args| {
        let v=script_value!(vm,args.phase); let mut phase=String::new();
        vm.string_with(v,|_,s|phase.push_str(s));
        let now=makepad_widgets::makepad_script::ScriptRunBudget::from_durations(Duration::ZERO,Duration::ZERO,512).hard_deadline;
        let budget=vm.bx.run_budget.unwrap();
        INIT_MARKS.with(|marks| marks.borrow_mut().push(json!({"phase":phase,"entry_elapsed_ms":(now-budget.hard_deadline+0.064)*1000.0,"instructions_until_sample":budget.instructions_until_sample})));
        NIL
    });
}

#[test]
#[ignore = "explicit bounded initialization diagnosis; not a substitute for the strict suite"]
fn initialization_phase_diagnostic() {
    let config:Value=read(std::env::var("RIPPLE_INIT_CONFIG").unwrap());
    makepad_widgets::widget_async::register_splash_isolate_mod(script_tools::script_mod);
    makepad_widgets::widget_async::register_splash_isolate_mod(init_probe_module);
    let mut results=Vec::new();
    for iteration in 0..config["iterations"].as_u64().unwrap() {
        for case in config["sources"].as_array().unwrap() {
            let original=std::fs::read_to_string(case["path"].as_str().unwrap()).unwrap();
            let mut source=format!("mod.ripple_init_probe.mark(\"first_statement_after_parse\")\n{original}");
            for (anchor,phase) in [("fn whole(t)","before_date_helpers"),("let Action =", "before_ui_prototypes"),("ui := SolidView", "before_ui_tree"),("\nstart_timeout(0.05", "after_ui_tree_before_boot_timer")] {
                assert!(source.contains(anchor),"diagnostic anchor missing: {anchor}");
                source=source.replacen(anchor,&format!("mod.ripple_init_probe.mark(\"{phase}\")\n{anchor}"),1);
            }
            if config["maximum_snapshot"].as_bool()==Some(true) && case["name"]=="candidate" {
                source=source.replacen("fn load_calendar(){", "fn load_calendar(){ mod.ripple_init_probe.mark(\"calendar_load_start\")",1);
                let anchor=if source.contains("}\r\nfn calendar_fail") { "}\r\nfn calendar_fail" } else { "}\nfn calendar_fail" };
                assert!(source.contains(anchor));
                source=source.replacen(anchor, "mod.ripple_init_probe.mark(\"calendar_load_end\")\n}\nfn calendar_fail",1);
            }
            let mut cx=Cx::new(Box::new(|_,_|{}));
            let ui=cx.with_vm(|vm| {makepad_widgets::script_mod(vm);let v=script_eval!(vm,{use mod.prelude.widgets.* View{card:=Splash{}}});WidgetRef::script_from_value(vm,v)});
            let card=ui.splash(&mut cx,ids!(card));
            let jail=evidence().join(format!("probe-{iteration}-{}",case["name"].as_str().unwrap()));std::fs::create_dir(&jail).unwrap();
            card.set_host_tag(&mut cx,Some("ripple".into()));card.set_sandbox_dir(&mut cx,Some(jail.clone()));card.set_policy(&mut cx,Some(vec![]),Some(2_000_000));
            for kind in ["cold_isolate_full_parse","warm_isolate_append_re_evaluation"] {
                INIT_MARKS.with(|m|m.borrow_mut().clear());
                let start=std::time::Instant::now();card.set_text(&mut cx,&source);let total=start.elapsed().as_micros();
                let marks=INIT_MARKS.with(|m|m.borrow().clone());
                let files:Vec<_>=std::fs::read_dir(&jail).unwrap().map(|x|x.unwrap().file_name().to_string_lossy().into_owned()).collect();
                let row=json!({"iteration":iteration,"case":case["name"],"kind":kind,"set_text_us":total,"marks":marks,"files_before_boot":files});
                eprintln!("INIT_PHASE_RESULT {row}");results.push(row);
                assert!(marks.iter().any(|m|m["phase"]=="after_ui_tree_before_boot_timer"),"initialization must reach the end marker");
                if config["maximum_snapshot"].as_bool()==Some(true) && case["name"]=="candidate" {
                    let events:Vec<_>=(0..32).map(|i|json!({"uid":format!("bounded-{i}"),"title":"界".repeat(80),"location":"地".repeat(80),"start":1792026000u64+i*900,"end":1792026900u64+i*900,"all_day":false})).collect();
                    std::fs::write(jail.join("external-calendar.json"),json!({"version":1,"revision":"max-32-diagnostic","source":"Synthetic bounded snapshot","imported_at":1791940000,"events":events}).to_string()).unwrap();
                    INIT_MARKS.with(|m|m.borrow_mut().clear());let start=std::time::Instant::now();
                    let completed=card.call_script_fn_with_strings(&mut cx,id!(load_calendar),&[]);
                    let marks=INIT_MARKS.with(|m|m.borrow().clone());
                    let load_finished=marks.iter().any(|m|m["phase"]=="calendar_load_end");
                    let row=json!({"iteration":iteration,"case":case["name"],"kind":"load_calendar_with_maximum_snapshot","from":kind,"dispatched":completed,"load_finished":load_finished,"elapsed_us":start.elapsed().as_micros(),"marks":marks});
                    eprintln!("INIT_PHASE_RESULT {row}");results.push(row);
                    assert!(completed && load_finished,"calendar validation must reach its end marker; dispatch alone is not success");
                }
                source.push_str("\n// diagnostic append for cached-parser re-evaluation\n");
            }
        }
    }
    write("initialization-phases.json",&json!({"classification":"INSTRUMENTED_DIAGNOSTIC_NOT_STRICT_ACCEPTANCE","results":results}));
}
