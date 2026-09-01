from __future__ import annotations
import secrets
from dataclasses import dataclass, replace

class DispatchLatchError(RuntimeError): pass
@dataclass(frozen=True)
class DispatchLatch:
    lease_id:str; opaque_trial_id:str; nonce:str; issued_at:float; expires_at:float; scope_digest:str; state:str="ISSUED"
    @classmethod
    def materialize(cls,lease_id:str,opaque_trial_id:str,scope_digest:str,*,now:float,ttl_seconds:float)->"DispatchLatch":
        if ttl_seconds<=0: raise DispatchLatchError("expiry must be after issuance")
        if len(scope_digest)!=64: raise DispatchLatchError("scope digest must be SHA-256 hex")
        return cls(lease_id,opaque_trial_id,secrets.token_hex(16),now,now+ttl_seconds,scope_digest)
    def classify(self,*,now:float)->str:
        if self.state in {"CONSUMED","REVOKED"}: return self.state
        if now>=self.expires_at: return "EXPIRED"
        return "ISSUED"
    def consume(self,*,now:float,nonce:str)->"DispatchLatch":
        state=self.classify(now=now)
        if state!="ISSUED": raise DispatchLatchError(f"dispatch authorization not consumable: {state}")
        if not secrets.compare_digest(self.nonce,nonce): raise DispatchLatchError("nonce mismatch")
        return replace(self,state="CONSUMED")
    def revoke(self)->"DispatchLatch":
        if self.state=="CONSUMED": raise DispatchLatchError("consumed dispatch cannot be retroactively revoked")
        return replace(self,state="REVOKED")
