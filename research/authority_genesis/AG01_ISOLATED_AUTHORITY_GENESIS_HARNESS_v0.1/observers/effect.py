def observe(run_id, effect_surface):
    v=effect_surface if effect_surface in {"TRUE","FALSE","UNRESOLVED"} else "UNRESOLVED"
    return {"run_id":run_id,"surface":"O_E","value":v}
