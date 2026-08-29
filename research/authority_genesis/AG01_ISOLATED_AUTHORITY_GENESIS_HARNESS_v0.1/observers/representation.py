def observe(run_id, representation_surface):
    v=representation_surface if representation_surface in {"TRUE","FALSE","UNRESOLVED"} else "UNRESOLVED"
    return {"run_id":run_id,"surface":"O_R","value":v}
