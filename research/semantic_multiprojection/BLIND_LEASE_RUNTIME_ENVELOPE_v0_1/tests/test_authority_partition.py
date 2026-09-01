import pytest
from src.authority_partition import AuthorityDenied, AuthorityPartition

def test_required_forbidden_crossings_are_denied():
    p=AuthorityPartition(); crossings=[("A_E","REVEAL_PERMUTATION"),("A_E","SCIENTIFIC_ADMIT"),("A_D","PROMOTE_PROPERLY"),("A_L","EXTRACT")]
    for role,action in crossings:
        with pytest.raises(AuthorityDenied): p.authorize(role,action)

def test_each_role_retains_own_positive_capability():
    p=AuthorityPartition()
    for role,action in [("A_L","HASH_VERIFY"),("A_D","CREATE_DISPATCH"),("A_E","ADJUDICATE"),("A_R","RECONCILE_SEALED_OBSERVATION"),("A_S","SCIENTIFIC_ABSTAIN"),("A_P","PROMOTE_PROPERLY")]: p.authorize(role,action)
