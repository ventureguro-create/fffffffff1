"""Safe Scheduler - picks next channel to process"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
from .safe_mode import is_safe_mode_active


async def pick_next_channel(db, policy: Dict[str, Any]) -> Dict[str, Any]:
    """Pick next channel to process based on stage and priority"""
    safe = await is_safe_mode_active(db, policy)
    if safe['active']:
        return {'channel': None, 'reason': 'SAFE_MODE', 'until': safe.get('until')}
    
    now = datetime.now(timezone.utc)
    
    # Order: CANDIDATE first, then PENDING, then QUALIFIED
    stage_order = ['CANDIDATE', 'PENDING', 'QUALIFIED']
    
    for stage in stage_order:
        ch = await db.tg_channel_states.find_one(
            {
                'stage': stage,
                'nextAllowedAt': {'$lte': now},
            },
            sort=[
                ('priority', 1),  # 0 is highest
                ('lastIngestAt', 1),  # older first
                ('lastCensusAt', 1),
            ]
        )
        
        if ch:
            return {'channel': ch, 'reason': 'OK'}
    
    return {'channel': None, 'reason': 'EMPTY'}


def compute_next_allowed_at(stage: str, priority: int, policy: Dict[str, Any]) -> datetime:
    """Compute next allowed processing time based on stage and priority"""
    now = datetime.now(timezone.utc)
    
    base_qualified = policy.get('qualifiedRefreshHours', 48)
    base_candidate = policy.get('candidateRetryHours', 24)
    
    if stage == 'QUALIFIED':
        # Priority 1 -> faster, 9 -> slower
        if priority <= 2:
            factor = 0.5
        elif priority <= 4:
            factor = 1.0
        elif priority <= 6:
            factor = 1.5
        else:
            factor = 2.5
        hours = max(12, round(base_qualified * factor))
        return now + timedelta(hours=hours)
    
    if stage in ('CANDIDATE', 'PENDING'):
        if priority <= 3:
            factor = 0.8
        elif priority <= 6:
            factor = 1.0
        else:
            factor = 1.6
        hours = max(6, round(base_candidate * factor))
        return now + timedelta(hours=hours)
    
    return now + timedelta(days=7)
