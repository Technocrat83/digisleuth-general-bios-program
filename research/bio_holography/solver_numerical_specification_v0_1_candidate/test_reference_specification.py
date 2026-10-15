import math
import unittest
from reference_laws import cohesive_lengths,contact_damage,contact_traction,contact_viscous_power,slit_conductance,fluid_edge_flux,membrane_flux,concentration,adhesive_edge_exists,conservative_merge,RG
from cohort_audit import audit_members


def member(embryo,dam,partition,batch):
    return {'embryo_id':embryo,'dam_id':dam,'litter_id':'litter_'+embryo,'harvest_event_id':'harvest_'+embryo,'culture_dish_id':'dish_'+embryo,'partition':partition,'collection_batch_id':batch,'acquisition_batch_id':batch,'treatment_batch_id':batch}


class ReferenceLawTests(unittest.TestCase):
    def test_cohesive_peak_and_completion(self):
        d0,df=cohesive_lengths(4,2,2)
        self.assertEqual((d0,df),(0.5,2))
        self.assertEqual(contact_traction(d0,0,0,4,2,2,0)[0],2)
        self.assertEqual(contact_traction(df,0,0,4,2,2,0)[0],0)

    def test_loading_work_equals_independent_quadrature(self):
        xs=[0,0.5,2]
        ys=[contact_traction(x,0,0,4,2,2,0)[0] for x in xs]
        work=sum((b-a)*(ya+yb)/2 for a,b,ya,yb in zip(xs,xs[1:],ys,ys[1:]))
        self.assertEqual(work,2)

    def test_unloading_retains_damage(self):
        loaded=contact_traction(1,0,0,4,2,2,0)
        unloaded=contact_traction(0.25,0,loaded[1],4,2,2,0)
        self.assertEqual(unloaded[2],loaded[2])
        self.assertLess(unloaded[0],4*0.25)

    def test_fully_failed_contact_cannot_recover_on_closure(self):
        self.assertEqual(contact_traction(0.1,0,2,4,2,2,0)[0],0)

    def test_dynamic_traction_may_exceed_equilibrium_peak(self):
        self.assertGreater(contact_traction(0.5,1,0,4,2,2,3)[0],2)

    def test_damping_dissipates_for_both_velocity_signs(self):
        self.assertEqual(contact_viscous_power(0.5,3,2),6)
        self.assertEqual(contact_viscous_power(0.5,3,-2),6)

    def test_invalid_contact_parameters_are_rejected(self):
        for args in [(1,4,1),(0,2,2),(4,2,float('nan'))]:
            with self.assertRaises(ValueError):cohesive_lengths(*args)

    def test_slit_conductance_is_cubic_in_aperture(self):
        a=slit_conductance(10,0.1,10,1)
        b=slit_conductance(10,0.2,10,1)
        self.assertAlmostEqual(b/a,8)

    def test_non_slender_bridge_refuses_slit_formula(self):
        with self.assertRaises(ValueError):slit_conductance(1,0.2,1,1)

    def test_hydraulic_and_solute_edge_flux_reverse_consistently(self):
        a=fluid_edge_flux(4,1,3,2,2,0.5)
        b=fluid_edge_flux(1,4,2,3,2,0.5)
        self.assertEqual(a,tuple(-x for x in b))

    def test_advection_uses_the_upstream_concentration(self):
        self.assertEqual(fluid_edge_flux(1,3,8,2,1,0),( -2,-4))

    def test_uniform_concentration_diffusion_is_zero(self):
        self.assertEqual(fluid_edge_flux(1,1,3,3,2,1),(0,0))

    def test_balanced_osmotic_and_hydrostatic_pressure_has_zero_water_flux(self):
        p=RG*300*(3-2)
        self.assertEqual(membrane_flux(p,0,3,2,1,1,0,1,300,0)[0],0)

    def test_active_solute_pumping_is_not_a_direct_water_source(self):
        a=membrane_flux(0,0,2,2,1,1,0,1,300,0)
        b=membrane_flux(0,0,2,2,1,1,0,1,300,5)
        self.assertEqual(a[0],b[0])
        self.assertEqual(b[1]-a[1],5)

    def test_internal_transfer_conserves_cell_and_fluid_inventories(self):
        q,j=membrane_flux(3,1,2,2,1,1,0.2,0.5,300,0.5)
        self.assertEqual(math.fsum([-q,q]),0)
        self.assertEqual(math.fsum([-j,j]),0)

    def test_invalid_membrane_reflection_is_rejected(self):
        with self.assertRaises(ValueError):membrane_flux(0,0,2,2,1,1,0,1.1,300,0)

    def test_nonpositive_cell_water_is_rejected_without_clipping(self):
        for v in (0,-1):
            with self.assertRaises(ValueError):concentration(1,v)

    def test_partial_failure_retains_an_adhesive_edge(self):
        self.assertTrue(adhesive_edge_exists([1,0.999]))
        self.assertFalse(adhesive_edge_exists([1,1]))

    def test_event_mapping_preserves_both_inventories(self):
        self.assertEqual(conservative_merge([0.1,0.2],[4,7]),(math.fsum([0.1,0.2]),11))


class CohortBoundaryTests(unittest.TestCase):
    def test_multiple_batches_do_not_make_one_dam_independent(self):
        r=audit_members([member('a','dam1','baseline_calibration','b1'),member('b','dam1','holdout_validation','b2')])
        self.assertEqual(r['metadata_group_audit'],'INVALID')
        self.assertGreater(r['acquisition_batch_entropy_nats'],0)
        self.assertEqual(r['counts']['dams'],1)
        self.assertIsNone(r['effective_biological_sample_size'])

    def test_shared_litter_rejects_split_even_with_different_dam_labels(self):
        a=member('a','d1','baseline_calibration','b1');b=member('b','d2','holdout_validation','b2')
        a['litter_id']=b['litter_id']='same_litter'
        self.assertTrue(any('litter_id' in x for x in audit_members([a,b])['invalid']))

    def test_shared_dish_is_a_cross_partition_exposure(self):
        a=member('a','d1','baseline_calibration','b1');b=member('b','d2','holdout_validation','b2')
        a['culture_dish_id']=b['culture_dish_id']='same_dish'
        self.assertTrue(any('culture_dish_id' in x for x in audit_members([a,b])['invalid']))

    def test_litter_dam_binding_is_consistent_within_one_partition(self):
        a=member('a','d1','baseline_calibration','b1');b=member('b','d2','baseline_calibration','b2')
        a['litter_id']=b['litter_id']='same_litter'
        self.assertEqual(audit_members([a,b])['metadata_group_audit'],'INVALID')

    def test_missing_dam_keeps_metadata_unresolved(self):
        a=member('a','d1','baseline_calibration','b1');a['dam_id']=None
        self.assertEqual(audit_members([a])['metadata_group_audit'],'UNRESOLVED')

    def test_metadata_completeness_never_grants_admission(self):
        r=audit_members([member('a','d1','baseline_calibration','b1'),member('b','d2','holdout_validation','b2')])
        self.assertEqual(r['metadata_group_audit'],'VALID_METADATA_ONLY')
        self.assertEqual(r['admission'],'PENDING_ADMISSION')
        self.assertEqual(r['calibration_gate'],'HOLD')

    def test_repeated_litters_from_one_dam_remain_grouped(self):
        r=audit_members([member('a','d1','baseline_calibration','b1'),member('b','d1','baseline_calibration','b2')])
        self.assertEqual(r['counts']['dams'],1)
        self.assertEqual(r['counts']['litters'],2)

    def test_duplicate_embryo_is_not_an_extra_replicate(self):
        a=member('a','d1','baseline_calibration','b1')
        r=audit_members([a,a.copy()])
        self.assertEqual(r['metadata_group_audit'],'INVALID')
        self.assertEqual(r['counts']['embryos'],1)

    def test_empty_cohort_remains_unmaterialized(self):
        r=audit_members([])
        self.assertEqual(r['metadata_group_audit'],'UNRESOLVED')
        self.assertEqual(r['counts']['dams'],0)

    def test_malformed_identity_does_not_create_a_lineage_cluster(self):
        a=member('a','d1','baseline_calibration','b1');a['dam_id']={'unverified':'d1'}
        r=audit_members([a])
        self.assertEqual(r['metadata_group_audit'],'UNRESOLVED')
        self.assertEqual(r['counts']['dams'],0)

    def test_non_object_member_is_rejected(self):
        self.assertEqual(audit_members([42])['metadata_group_audit'],'INVALID')

    def test_shared_batch_invalidates_an_unseen_batch_claim(self):
        a=member('a','d1','baseline_calibration','same_batch');b=member('b','d2','holdout_validation','same_batch')
        self.assertEqual(audit_members([a,b],True)['metadata_group_audit'],'INVALID')
        self.assertEqual(audit_members([a,b],False)['metadata_group_audit'],'VALID_METADATA_ONLY')


if __name__=='__main__':unittest.main()
