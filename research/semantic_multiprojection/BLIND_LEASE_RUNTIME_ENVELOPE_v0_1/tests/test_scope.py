from src.referential_scope import verify_referential_scope

def test_scope_requires_all_five_coordinates_and_mp0_mp6():
    coords={"identity":1,"meaning":1,"provenance":1,"jurisdiction":1,"authority":1}; result=verify_referential_scope(coords,{"Omega_H":coords,"Omega_M":coords},{f"MP{i}_X" for i in range(7)}); assert result.closed

def test_scope_missing_chamber_is_not_closed():
    coords={"identity":1,"meaning":1,"provenance":1,"jurisdiction":1,"authority":1}; result=verify_referential_scope(coords,{"Omega_H":coords},{f"MP{i}_X" for i in range(6)}); assert not result.closed
