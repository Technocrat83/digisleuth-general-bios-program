"""Algebraic reference functions only. No time integrator or tissue solver."""
from math import isfinite, fsum

RG = 8.31446261815324


def number(x, *, positive=False, nonnegative=False):
    if isinstance(x,bool) or not isinstance(x,(float,int)) or not isfinite(x):
        raise ValueError('finite real value required')
    if positive and x <= 0 or nonnegative and x < 0:
        raise ValueError('value outside admissible range')
    return x


def cohesive_lengths(stiffness, peak, work):
    for x in (stiffness,peak,work):number(x,positive=True)
    onset,complete=peak/stiffness,2*work/peak
    if complete <= onset:
        raise ValueError('complete opening must exceed damage onset')
    return onset,complete


def contact_damage(kappa,stiffness,peak,work):
    number(kappa,nonnegative=True)
    onset,complete=cohesive_lengths(stiffness,peak,work)
    if kappa <= onset:return 0.0
    if kappa >= complete:return 1.0
    return complete*(kappa-onset)/(kappa*(complete-onset))


def contact_traction(opening,velocity,accepted_history,stiffness,peak,work,viscosity):
    for x in (opening,accepted_history,viscosity):number(x,nonnegative=True)
    number(velocity)
    history=max(opening,accepted_history)
    damage=contact_damage(history,stiffness,peak,work)
    return ((1-damage)*(stiffness*opening+viscosity*velocity),history,damage)


def contact_viscous_power(damage,viscosity,velocity):
    number(damage);number(viscosity,nonnegative=True);number(velocity)
    if not 0 <= damage <= 1:raise ValueError('invalid damage')
    return (1-damage)*viscosity*velocity**2


def slit_conductance(width,height,length,viscosity):
    for x in (width,height,length,viscosity):number(x,positive=True)
    if height/length > 0.1 or height/width > 0.1:
        raise ValueError('slit geometry outside branch scope')
    return width*height**3/(12*viscosity*length)


def fluid_edge_flux(p_a,p_b,c_a,c_b,conductance,diffusive_conductance):
    for x in (p_a,p_b):number(x)
    for x in (c_a,c_b,conductance,diffusive_conductance):number(x,nonnegative=True)
    water=conductance*(p_a-p_b)
    donor=c_a if water >= 0 else c_b
    solute=diffusive_conductance*(c_a-c_b)+water*donor
    return water,solute


def membrane_flux(p_i,p_q,c_i,c_q,area,lp,ps,reflection,temperature,pump_rate):
    for x in (p_i,p_q,pump_rate):number(x)
    for x in (c_i,c_q,lp,ps):number(x,nonnegative=True)
    for x in (area,temperature):number(x,positive=True)
    number(reflection)
    if not 0 <= reflection <= 1:raise ValueError('reflection coefficient outside [0,1]')
    water=lp*area*((p_i-p_q)-reflection*RG*temperature*(c_i-c_q))
    donor=c_i if water >= 0 else c_q
    solute=area*(pump_rate+ps*(c_i-c_q))+(1-reflection)*donor*water
    return water,solute


def concentration(amount,water_volume):
    number(amount,nonnegative=True);number(water_volume,positive=True)
    return amount/water_volume


def adhesive_edge_exists(patch_damage):
    for d in patch_damage:
        number(d)
        if not 0 <= d <= 1:raise ValueError('invalid damage')
    return any(d < 1 for d in patch_damage)


def conservative_merge(water,solute):
    if len(water)!=len(solute) or len(water)<2:
        raise ValueError('matching arrays for at least two compartments required')
    for values in (water,solute):
        for v in values:number(v,nonnegative=True)
    return fsum(water),fsum(solute)
