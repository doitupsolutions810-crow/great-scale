"""Great Scale LXXXIII: dependency-aware certificate status propagation."""
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

class Status(str, Enum):
    VALID = "valid"
    STALE = "stale_requires_revalidation"
    INVALID = "invalid"

@dataclass
class Certificate:
    certificate_id: str
    calibration_version: int
    dependencies: tuple[str, ...] = ()
    status: Status = Status.VALID
    evidence_note: str = ""

@dataclass
class ProvenanceGraph:
    certificates: dict[str, Certificate] = field(default_factory=dict)

    def add(self, cert: Certificate) -> None:
        if not cert.certificate_id or cert.certificate_id in self.certificates:
            raise ValueError("certificate ID must be nonempty and unique")
        missing = [d for d in cert.dependencies if d not in self.certificates]
        if missing:
            raise ValueError(f"dependencies must be added first: {missing}")
        if cert.certificate_id in cert.dependencies:
            raise ValueError("certificate cannot depend on itself")
        if any(self.certificates[d].status is not Status.VALID for d in cert.dependencies):
            cert.status = Status.STALE
        self.certificates[cert.certificate_id] = cert

    def revoke_root(self, certificate_id: str, reason: str = "upstream assumption failed") -> list[str]:
        """Invalidate root; mark transitive descendants stale, not unrelated nodes."""
        if certificate_id not in self.certificates:
            raise KeyError(certificate_id)
        root = self.certificates[certificate_id]
        root.status = Status.INVALID
        root.evidence_note = reason
        affected = [certificate_id]
        queue = deque([certificate_id])
        seen = {certificate_id}
        while queue:
            parent = queue.popleft()
            for cert in self.certificates.values():
                if parent in cert.dependencies and cert.certificate_id not in seen:
                    seen.add(cert.certificate_id)
                    cert.status = Status.STALE
                    cert.evidence_note = f"depends on invalidated certificate {parent}"
                    affected.append(cert.certificate_id)
                    queue.append(cert.certificate_id)
        return affected

    def revalidate(self, certificate_id: str, new_calibration_version: int, evidence_note: str) -> None:
        """Revalidate a node only if all direct dependencies are currently valid."""
        if certificate_id not in self.certificates:
            raise KeyError(certificate_id)
        if new_calibration_version < 1:
            raise ValueError("calibration version must be positive")
        cert = self.certificates[certificate_id]
        bad = [d for d in cert.dependencies if self.certificates[d].status is not Status.VALID]
        if bad:
            raise ValueError(f"cannot revalidate while dependencies are not valid: {bad}")
        cert.calibration_version = new_calibration_version
        cert.status = Status.VALID
        cert.evidence_note = evidence_note

    def snapshot(self) -> dict:
        return {key: {"status": cert.status.value, "calibration_version": cert.calibration_version,
                      "dependencies": list(cert.dependencies), "evidence_note": cert.evidence_note}
                for key, cert in self.certificates.items()}
