"""Rest screens for the D&D Manager application."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


class ShortRestScreen(Screen):
    """Screen for taking a short rest with hit dice spending."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm Rest"),
        Binding("y", "confirm_yes", "Yes, Rest"),
        Binding("r", "roll_hit_die", "Roll Hit Die"),
        Binding("+", "add_die", "Spend +1 Die"),
        Binding("-", "remove_die", "Spend -1 Die"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.dice_to_spend = 0
        self.healing_rolls: list[int] = []
        self.total_healing = 0
        self.awaiting_confirmation = False

    def compose(self) -> ComposeResult:
        c = self.character
        hp = c.combat.hit_points
        hd_display = c.combat.get_hit_dice_display()

        yield Header()
        yield Container(
            Static("Short Rest", classes="title"),
            Static(f"{c.name} - HP: {hp.current}/{hp.maximum}", classes="subtitle"),
            Vertical(
                Static("SHORT REST OPTIONS", classes="panel-title"),
                Static(f"  Hit Dice Available: {hd_display}", id="hd-info"),
                Static(f"  CON Modifier: +{c.abilities.constitution.modifier}", id="con-info"),
                Static(""),
                Static("  Dice to Spend: 0", id="dice-count"),
                Static(""),
                Static("  \\[+] Add a die  \\[-] Remove a die", classes="option"),
                Static("  \\[R] Roll selected dice", classes="option"),
                Static(""),
                Static("  HEALING ROLLS:", classes="section-header"),
                VerticalScroll(id="healing-rolls", classes="healing-list"),
                Static(""),
                Static("  Total Healing: 0", id="total-healing"),
                Static(""),
                Static("", id="confirm-prompt"),
                classes="panel rest-panel",
            ),
            id="short-rest-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize display."""
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh all display elements."""
        pool = self.character.combat.hit_dice_pool
        hd = self.character.combat.hit_dice

        # Update dice count
        dice_widget = self.query_one("#dice-count", Static)
        dice_widget.update(f"  Dice to Spend: {self.dice_to_spend}")

        # Update hit dice info
        hd_widget = self.query_one("#hd-info", Static)
        if pool and pool.pools:
            # Show pool format for multiclass
            total_remaining = pool.remaining - self.dice_to_spend
            hd_widget.update(f"  Hit Dice Available: {total_remaining}/{pool.total} ({pool.get_display_string()})")
        else:
            available = hd.remaining - self.dice_to_spend
            hd_widget.update(f"  Hit Dice Available: {available}/{hd.total} ({hd.die})")

        # Update healing rolls
        rolls_widget = self.query_one("#healing-rolls", VerticalScroll)
        rolls_widget.remove_children()
        if self.healing_rolls:
            con_mod = self.character.abilities.constitution.modifier
            for i, roll_data in enumerate(self.healing_rolls):
                # Handle both old format (int) and new format (int, die)
                if isinstance(roll_data, tuple):
                    roll, die = roll_data
                    total = max(1, roll + con_mod)
                    rolls_widget.mount(Static(f"    {die}: {roll} + {con_mod} (CON) = {total} HP"))
                else:
                    roll = roll_data
                    total = max(1, roll + con_mod)
                    rolls_widget.mount(Static(f"    Die {i+1}: {roll} + {con_mod} (CON) = {total} HP"))
        else:
            rolls_widget.mount(Static("    (No dice rolled yet)"))

        # Update total healing
        total_widget = self.query_one("#total-healing", Static)
        total_widget.update(f"  Total Healing: {self.total_healing}")

        # Update confirm prompt
        confirm_widget = self.query_one("#confirm-prompt", Static)
        if self.awaiting_confirmation:
            confirm_widget.update("  ➤ Take short rest? Press \\[Y] to confirm, \\[Esc] to cancel")
        else:
            confirm_widget.update("  Press \\[Enter] to take short rest  \\[Esc] to cancel")

    def action_add_die(self) -> None:
        """Add a hit die to spend."""
        pool = self.character.combat.hit_dice_pool
        hd = self.character.combat.hit_dice

        # Check actual available dice (pool if multiclass, simple hd otherwise)
        available = pool.remaining if (pool and pool.pools) else hd.remaining

        if self.dice_to_spend < available:
            self.dice_to_spend += 1
            self._refresh_display()
        else:
            self.notify("No more hit dice available!", severity="warning")

    def action_remove_die(self) -> None:
        """Remove a hit die from spending."""
        if self.dice_to_spend > 0:
            self.dice_to_spend -= 1
            self._refresh_display()

    def action_roll_hit_die(self) -> None:
        """Roll the selected hit dice for healing."""
        if self.dice_to_spend == 0:
            self.notify("Add dice to spend first! Press \\[+]", severity="warning")
            return

        from dnd_manager.dice import DiceRoller

        roller = DiceRoller()
        con_mod = self.character.abilities.constitution.modifier
        pool = self.character.combat.hit_dice_pool

        # Roll each die
        self.healing_rolls = []
        self.total_healing = 0

        # Track remaining dice during roll preview (don't modify actual pool yet)
        if pool and pool.pools:
            temp_remaining = {die: p.remaining for die, p in pool.pools.items()}
        else:
            temp_remaining = None

        for _ in range(self.dice_to_spend):
            # For multiclass, use pool (largest die first); else use simple die
            if temp_remaining is not None:
                # Get largest available die type from temp tracking
                die = None
                for d in sorted(temp_remaining.keys(), key=lambda x: int(x[1:]), reverse=True):
                    if temp_remaining[d] > 0:
                        die = d
                        temp_remaining[d] -= 1  # Track that we're using this die
                        break
                if die is None:
                    # No dice available - shouldn't happen if add_die validates correctly
                    self.notify("No hit dice available!", severity="error")
                    return
            else:
                die = self.character.combat.hit_dice.die

            result = roller.roll(f"1{die}")
            roll = result.total
            self.healing_rolls.append((roll, die))  # Track die type used
            healing = max(1, roll + con_mod)  # Minimum 1 HP per die
            self.total_healing += healing

        self.notify(f"Rolled {self.dice_to_spend} hit dice for {self.total_healing} HP!")
        self._refresh_display()

    def action_confirm(self) -> None:
        """Show confirmation prompt."""
        self.awaiting_confirmation = True
        self._refresh_display()

    def action_confirm_yes(self) -> None:
        """Actually execute the short rest after confirmation."""
        if not self.awaiting_confirmation:
            return

        c = self.character

        # Apply healing
        if self.total_healing > 0:
            hp = c.combat.hit_points
            old_hp = hp.current
            hp.current = min(hp.maximum, hp.current + self.total_healing)
            actual_healing = hp.current - old_hp

            # Spend hit dice (from pool if multiclassed)
            pool = c.combat.hit_dice_pool
            if pool and pool.pools:
                # Spend each die that was rolled
                for roll_data in self.healing_rolls:
                    if isinstance(roll_data, tuple):
                        _, die = roll_data
                        pool.spend(die)
                # Sync simple hit_dice for backward compat
                c.combat.hit_dice = pool.to_single()
            else:
                c.combat.hit_dice.remaining -= self.dice_to_spend

            self.notify(f"Short rest complete! Healed {actual_healing} HP", severity="information")
        else:
            self.notify("Short rest complete!", severity="information")

        # Recover short rest features
        for feature in c.features:
            if feature.uses and feature.recharge in ("short rest", "short_rest"):
                feature.used = 0

        self.app.save_character()
        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel the short rest."""
        if self.awaiting_confirmation:
            self.awaiting_confirmation = False
            self._refresh_display()
        else:
            self.app.pop_screen()


class LongRestScreen(Screen):
    """Screen for taking a long rest with full recovery summary."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm Rest"),
        Binding("y", "confirm_yes", "Yes, Rest"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.awaiting_confirmation = False

    def compose(self) -> ComposeResult:
        c = self.character
        hp = c.combat.hit_points
        pool = c.combat.hit_dice_pool
        hd = c.combat.hit_dice

        # Calculate hit dice info
        if pool and pool.pools:
            hd_total = pool.total
            hd_display = c.combat.get_hit_dice_display()
        else:
            hd_total = hd.total
            hd_display = f"{hd.remaining}/{hd.total}{hd.die}"

        yield Header()
        yield Container(
            Static("Long Rest", classes="title"),
            Static(f"{c.name} - Level {c.total_level} {c.primary_class.name}", classes="subtitle"),
            Vertical(
                Static("LONG REST RECOVERY", classes="panel-title"),
                Static(""),
                Static("  The following will be restored:", classes="section-header"),
                Static(""),
                Static(f"  ♥ HP: {hp.current} → {hp.maximum} (full)", id="hp-restore"),
                Static(f"  ⬡ Hit Dice: +{max(1, hd_total // 2)} (current: {hd_display})", id="hd-restore"),
                Static(id="spell-restore"),
                Static(id="feature-restore"),
                Static(""),
                Static("  Temporary HP will be cleared", classes="note"),
                Static("  Death saves will be reset", classes="note"),
                Static(""),
                Static("", id="confirm-prompt"),
                classes="panel rest-panel",
            ),
            id="long-rest-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Calculate and display restoration summary."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with restoration info."""
        c = self.character

        # Spell slots restoration
        spell_widget = self.query_one("#spell-restore", Static)
        if c.spellcasting.ability:
            spell_widget.update("  ✦ All spell slots restored")
        else:
            spell_widget.update("  ✦ (No spellcasting)")

        # Features restoration
        feature_widget = self.query_one("#feature-restore", Static)
        long_rest_features = [
            f.name for f in c.features
            if f.uses and f.recharge in ("long rest", "long_rest", "daily")
            and f.used > 0
        ]
        if long_rest_features:
            if len(long_rest_features) <= 3:
                feature_widget.update(f"  ★ Features: {', '.join(long_rest_features)}")
            else:
                feature_widget.update(f"  ★ {len(long_rest_features)} features with uses restored")
        else:
            feature_widget.update("  ★ All feature uses restored")

        # Update confirm prompt
        confirm_widget = self.query_one("#confirm-prompt", Static)
        if self.awaiting_confirmation:
            confirm_widget.update("  ➤ Take long rest? Press \\[Y] to confirm, \\[Esc] to cancel")
        else:
            confirm_widget.update("  Press \\[Enter] to take long rest  \\[Esc] to cancel")

    def action_confirm(self) -> None:
        """Show confirmation prompt."""
        self.awaiting_confirmation = True
        self._update_display()

    def action_confirm_yes(self) -> None:
        """Actually execute the long rest after confirmation."""
        if not self.awaiting_confirmation:
            return

        c = self.character
        pool = c.combat.hit_dice_pool
        hd = c.combat.hit_dice

        # Store old values for summary (check pool for multiclass)
        old_hp = c.combat.hit_points.current
        old_hd = pool.remaining if (pool and pool.pools) else hd.remaining

        # Apply long rest
        c.long_rest()

        # Save
        self.app.save_character()

        # Calculate actual restoration (check pool for multiclass)
        pool = c.combat.hit_dice_pool  # Refresh reference after long_rest
        hd = c.combat.hit_dice
        new_hd = pool.remaining if (pool and pool.pools) else hd.remaining
        hp_healed = c.combat.hit_points.current - old_hp
        hd_restored = new_hd - old_hd

        self.notify(f"Long rest complete! HP +{hp_healed}, Hit Dice +{hd_restored}", severity="information")
        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel the long rest."""
        if self.awaiting_confirmation:
            self.awaiting_confirmation = False
            self._update_display()
        else:
            self.app.pop_screen()
