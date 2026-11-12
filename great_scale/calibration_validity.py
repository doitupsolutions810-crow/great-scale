"""LXXXII: bounded-error calibration validity state machine."""
from dataclasses import dataclass
from enum import Enum
import math

class CalibrationState(str, Enum):
    VALID = "valid"
    DEGRADED = "degraded_or_indeterminate"
    INVALID = "invalid"

@dataclass(frozen=True)
class CalibrationAssessment:
    state: CalibrationState
    residual_lower: float
    residual_upper: float
    threshold: float
    reason: str

def assess_calibration(residual: float, uncertainty: float, max_residual: float) -> CalibrationAssessment:
    """Classify a residual interval; assumes |observed - true| <= uncertainty."""
    if not all(math.isfinite(v) for v in (residual, uncertainty, max_residual)):
        raise ValueError("inputs must be finite")
    if uncertainty < 0 or max_residual <= 0:
        raise ValueError("uncertainty must be nonnegative and threshold positive")
    magnitude = abs(residual)
    lower, upper = max(0.0, magnitude - uncertainty), magnitude + uncertainty
    if upper < max_residual:
        state, reason = CalibrationState.VALID, "entire residual interval is below limit"
    elif lower > max_residual:
        state, reason = CalibrationState.INVALID, "entire residual interval exceeds limit"
    else:
        state, reason = CalibrationState.DEGRADED, "residual interval overlaps or touches limit"
    return CalibrationAssessment(state, lower, upper, max_residual, reason)

@dataclass
class CalibrationMonitor:
    """Breach invalidates immediately; recovery needs K consecutive clean checks."""
    max_residual: float
    recovery_checks: int = 3
    state: CalibrationState = CalibrationState.DEGRADED
    clean_streak: int = 0
    calibration_version: int = 1

    def __post_init__(self):
        if not math.isfinite(self.max_residual) or self.max_residual <= 0:
            raise ValueError("max_residual must be finite and positive")
        if self.recovery_checks < 1:
            raise ValueError("recovery_checks must be >= 1")

    def update(self, residual: float, uncertainty: float) -> CalibrationState:
        assessment = assess_calibration(residual, uncertainty, self.max_residual)
        if assessment.state is CalibrationState.INVALID:
            self.state, self.clean_streak = CalibrationState.INVALID, 0
        elif assessment.state is CalibrationState.DEGRADED:
            if self.state is not CalibrationState.INVALID:
                self.state = CalibrationState.DEGRADED
            self.clean_streak = 0
        else:
            self.clean_streak += 1
            if self.clean_streak >= self.recovery_checks:
                self.state = CalibrationState.VALID
            elif self.state is not CalibrationState.INVALID:
                self.state = CalibrationState.DEGRADED
        return self.state

    def recalibrate(self) -> int:
        """Create a new provenance version; the new calibration starts unvalidated."""
        self.calibration_version += 1
        self.state, self.clean_streak = CalibrationState.DEGRADED, 0
        return self.calibration_version
