import pygame
import random
from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet
from .sounds import SoundEffects

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
# Enemy speed (pixels per frame) and enemy fire chance (per enemy, per frame)
DIFFICULTIES = {
    "Easy":   {"speed": 1.0, "fire_chance": 0.005},
    "Medium": {"speed": 1.5, "fire_chance": 0.010},  # the original values
    "Hard":   {"speed": 2.2, "fire_chance": 0.018},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 60)
        self.quit_requested = False
        self.sounds = SoundEffects()

        self.start_game("Medium")

    def start_game(self, difficulty):
        """Reset everything for a fresh round at the chosen difficulty."""
        settings = DIFFICULTIES[difficulty]
        self.difficulty = difficulty

        self.player = Player(self.width // 2 - 20, self.height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(self.width, speed=settings["speed"])

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        self.enemy_fire_chance = settings["fire_chance"]

        self.score = 0
        self.game_over = False

    def handle_event(self, event):
    # On the game-over screen, wait for Enter or Esc, then ask main.py to quit
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.start_game("Easy")
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.start_game("Medium")
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.start_game("Hard")
                elif event.key == pygame.K_ESCAPE:
                    self.quit_requested = True
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2
                self.player_bullets.append(Bullet(bullet_x, self.player.y, direction=-1))
                self._shoot_cooldown = 15
                self.sounds.play("fire")

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    def update(self):
        if self.game_over:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        self.enemy_grid.move()

        for enemy in self.enemy_grid.alive_enemies():
            if random.random() < self.enemy_fire_chance:
                bullet_x = enemy.x + enemy.width // 2
                self.enemy_bullets.append(Bullet(bullet_x, enemy.y + enemy.height, direction=1))

        for bullet in self.player_bullets:
            bullet.move()
        for bullet in self.enemy_bullets:
            bullet.move()

        self.player_bullets = [b for b in self.player_bullets if not b.off_screen(self.height)]
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.off_screen(self.height)]

        # Check player bullets against enemies without modifying the list
        # while iterating over it. Bullets that hit nothing are kept.
        remaining_bullets = []
        for bullet in self.player_bullets:
            bullet_rect = bullet.rect()
            hit = False
            for enemy in self.enemy_grid.alive_enemies():
                if bullet_rect.colliderect(enemy.rect()):
                    enemy.alive = False
                    self.score += 1
                    self.sounds.play("explosion")
                    hit = True
                    break  # one bullet destroys at most one enemy
            if not hit:
                remaining_bullets.append(bullet)
        self.player_bullets = remaining_bullets

        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                break

        if self.enemy_grid.reached_bottom(self.player.y):
            self.game_over = True
            
        if self.game_over:
            self.sounds.play("game_over")

    def render(self, screen):
        pygame.draw.rect(screen, GREEN, self.player.rect())

        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(screen, WHITE, enemy.rect())

        for bullet in self.player_bullets:
            pygame.draw.rect(screen, WHITE, bullet.rect())
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self._draw_game_over(screen)

    def _draw_game_over(self, screen):
        # Dim the frozen game behind the message
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.big_font.render("GAME OVER", True, RED)
        score = self.font.render(f"Final Score: {self.score}", True, WHITE)
        play = self.font.render("Play again - choose difficulty:", True, WHITE)
        options = self.font.render("1 Easy     2 Medium     3 Hard", True, GREEN)
        exit_text = self.font.render("Esc to exit", True, WHITE)

        cx = self.width // 2
        mid = self.height // 2
        screen.blit(title, title.get_rect(center=(cx, mid - 90)))
        screen.blit(score, score.get_rect(center=(cx, mid - 20)))
        screen.blit(play, play.get_rect(center=(cx, mid + 50)))
        screen.blit(options, options.get_rect(center=(cx, mid + 95)))
        screen.blit(exit_text, exit_text.get_rect(center=(cx, mid + 150)))
