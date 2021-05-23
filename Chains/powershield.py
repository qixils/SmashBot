import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain

class Powershield(Chain):
    def __init__(self, hold=False, zpress=False):
        self.hold = hold
        self.zpress = zpress

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        # Don't try to shield in the air
        if not smashbot_state.on_ground:
            self.interruptible = True
            controller.empty_input()
            return

        # FireFox is different
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID] and opponent_state.character in [Character.FOX, Character.FALCO]

        # If we get to cooldown, let go
        attackstate = self.framedata.attack_state(opponent_state.character, opponent_state.action, opponent_state.action_frame)
        if attackstate in [melee.enums.AttackState.COOLDOWN, melee.enums.AttackState.NOT_ATTACKING] \
                and len(gamestate.projectiles) == 0 and not firefox:
            self.interruptible = True
            controller.empty_input()
            return

        # Hold onto the shield until the attack is done
        if self.hold:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            controller.press_button(Button.BUTTON_L)
            return

        # Also hold the shield in case we pressed too soon and opponent is still attacking
        if attackstate == melee.AttackState.ATTACKING and smashbot_state.action in [Action.SHIELD_REFLECT, Action.SHIELD]:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            controller.press_button(Button.BUTTON_L)
            return

        # We're done if we are in shield release
        if smashbot_state.action == Action.SHIELD_RELEASE:
            self.interruptible = True
            controller.empty_input()
            return

        isshielding = smashbot_state.action == Action.SHIELD \
            or smashbot_state.action == Action.SHIELD_START \
            or smashbot_state.action == Action.SHIELD_REFLECT \
            or smashbot_state.action == Action.SHIELD_STUN \
            or smashbot_state.action == Action.SHIELD_RELEASE

        # If we're in shield stun, we can let go
        if smashbot_state.action == Action.SHIELD_STUN:
            if smashbot_state.hitlag_left > 0:
                self.interruptible = False
                controller.release_button(Button.BUTTON_A)
                controller.release_button(Button.BUTTON_Z)
                controller.release_button(Button.BUTTON_L)
                if controller.prev.main_stick[0] == 0.5:
                    controller.tilt_analog(Button.BUTTON_MAIN, int(opponent_state.position.x > smashbot_state.position.x), 0.5)
                else:
                    controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
                return
            else:
                self.interruptible = True
                controller.empty_input()
                return

        # If we already pressed L last frame, let go
        if controller.prev.button[Button.BUTTON_L]:
            controller.empty_input()
            return

        if not isshielding:
            self.interruptible = False
            if self.zpress and controller.prev.button[Button.BUTTON_A]:
                controller.press_button(Button.BUTTON_Z)
            controller.press_button(Button.BUTTON_L)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return

        self.interruptible = True
        controller.empty_input()
