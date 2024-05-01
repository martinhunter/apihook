DEBUG_API_HOOK = False  # log more info. exp: each injection triggered

# 10: each func/object can only be injected once globally, and will not be replaced by later setter
# TODO: 20: each func/object can only be injected once globally, but will be replaced by later setter
# 30: func/object can be injected multiple times at multi_hooker level, but the same func in wrapped multi_hooker will not be injected
# TODO: 40: func/object can be injected multiple times at multi_hooker level, the same func in wrapped multi_hooker will replace outer, and outer will be set after wrapped exit.
# 50: each func/object can be injected multiple times without limit
INJECTION_LEVEL_GLOBAL = 10
INJECTION_LEVEL_MULTI = 30
INJECTION_LEVEL_SINGLE = 50

INJECTION_LEVEL = INJECTION_LEVEL_MULTI
