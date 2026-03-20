"""
Emotion to Live2D parameter mapping.
Maps LLM emotion labels to Live2D Cubism model parameters.
"""

EMOTION_MAP = {
    "neutral": {
        "ParamMouthForm": 0.0,
        "ParamEyeLOpen": 1.0,
        "ParamEyeROpen": 1.0,
        "ParamBrowLY": 0.0,
        "ParamBrowRY": 0.0,
        "ParamBodyAngleX": 0.0,
        "ParamBodyAngleZ": 0.0,
        "ParamAngleX": 0.0,
        "ParamAngleY": 0.0,
        "ParamAngleZ": 0.0,
    },
    "happy": {
        "ParamMouthForm": 1.0,
        "ParamEyeLOpen": 0.7,
        "ParamEyeROpen": 0.7,
        "ParamBrowLY": 0.3,
        "ParamBrowRY": 0.3,
        "ParamBodyAngleZ": 2.0,
        "ParamAngleX": 0.0,
        "ParamAngleY": 0.0,
        "ParamAngleZ": 3.0,
    },
    "amused": {
        "ParamMouthForm": 1.0,
        "ParamMouthOpenY": 0.5,
        "ParamEyeLOpen": 0.5,
        "ParamEyeROpen": 0.5,
        "ParamBrowLY": 0.5,
        "ParamBrowRY": 0.5,
        "ParamBodyAngleZ": -3.0,
        "ParamAngleX": -5.0,
        "ParamAngleZ": -3.0,
    },
    "surprised": {
        "ParamMouthForm": -0.5,
        "ParamMouthOpenY": 0.8,
        "ParamEyeLOpen": 1.3,
        "ParamEyeROpen": 1.3,
        "ParamBrowLY": 1.0,
        "ParamBrowRY": 1.0,
        "ParamBodyAngleZ": 0.0,
        "ParamAngleY": -3.0,
    },
    "sad": {
        "ParamMouthForm": -0.7,
        "ParamEyeLOpen": 0.6,
        "ParamEyeROpen": 0.6,
        "ParamBrowLY": -0.5,
        "ParamBrowRY": -0.5,
        "ParamBodyAngleZ": -2.0,
        "ParamAngleX": 5.0,
        "ParamAngleY": 5.0,
    },
    "thinking": {
        "ParamMouthForm": -0.2,
        "ParamEyeLOpen": 0.8,
        "ParamEyeROpen": 0.8,
        "ParamBrowLY": -0.3,
        "ParamBrowRY": 0.5,
        "ParamAngleX": 10.0,
        "ParamAngleY": 5.0,
        "ParamBodyAngleZ": 3.0,
    },
    "excited": {
        "ParamMouthForm": 1.0,
        "ParamMouthOpenY": 0.7,
        "ParamEyeLOpen": 1.2,
        "ParamEyeROpen": 1.2,
        "ParamBrowLY": 0.8,
        "ParamBrowRY": 0.8,
        "ParamBodyAngleZ": -5.0,
        "ParamAngleZ": -5.0,
    },
    "empathetic": {
        "ParamMouthForm": 0.3,
        "ParamEyeLOpen": 0.8,
        "ParamEyeROpen": 0.8,
        "ParamBrowLY": -0.2,
        "ParamBrowRY": -0.2,
        "ParamAngleY": -3.0,
        "ParamBodyAngleZ": 2.0,
    },
    "angry": {
        "ParamMouthForm": -1.0,
        "ParamEyeLOpen": 0.7,
        "ParamEyeROpen": 0.7,
        "ParamBrowLY": -1.0,
        "ParamBrowRY": -1.0,
        "ParamBodyAngleX": -5.0,
        "ParamAngleX": -3.0,
    },
}


def get_emotion_params(emotion: str, intensity: float = 1.0) -> dict:
    """Get Live2D parameters for a given emotion, scaled by intensity."""
    base = EMOTION_MAP.get("neutral", {})
    target = EMOTION_MAP.get(emotion, base)

    result = {}
    for key in set(list(base.keys()) + list(target.keys())):
        base_val = base.get(key, 0.0)
        target_val = target.get(key, 0.0)
        result[key] = base_val + (target_val - base_val) * intensity

    return result


def blend_params(current: dict, target: dict, factor: float = 0.1) -> dict:
    """Smoothly interpolate between two expression states."""
    result = {}
    for key in set(list(current.keys()) + list(target.keys())):
        curr_val = current.get(key, 0.0)
        tgt_val = target.get(key, 0.0)
        result[key] = curr_val + (tgt_val - curr_val) * factor
    return result
