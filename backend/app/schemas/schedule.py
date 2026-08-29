from datetime import date, time

from pydantic import BaseModel, Field, model_validator


class ScheduleRequest(BaseModel):
    day_of_week: int = Field(ge=0, le=6, description="Python weekday: Monday=0, Sunday=6")
    start_time: time
    end_time: time
    appointment_duration: int = Field(gt=0, le=1440)
    break_start: time | None = None
    break_end: time | None = None
    is_available: bool = True

    @model_validator(mode="after")
    def validate_schedule_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        if (self.break_start is None) != (self.break_end is None):
            raise ValueError("Break start and break end must be provided together")
        if self.break_start is not None and self.break_end is not None:
            if self.break_start >= self.break_end:
                raise ValueError("Break start must be before break end")
            if self.break_start < self.start_time or self.break_end > self.end_time:
                raise ValueError("Break must fall inside working hours")
        return self


class ScheduleResponse(ScheduleRequest):
    id: int
    doctor_id: int


class AvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    available_slots: list[str]


class WeeklyAvailabilityResponse(BaseModel):
    doctor_id: int
    is_active: bool
    schedules: list[ScheduleResponse]
