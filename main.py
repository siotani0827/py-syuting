import pygame
import collections

# --- 設定 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 60

# --- カラー定義 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # 自機の設定
        self.player_pos = [100, 240]
        self.history = collections.deque(maxlen=100) # 過去の座標を記録（オプション用）
        
        # パワーアップ関連
        self.power_gauge = 0 # 0:なし, 1:SPEED, 2:MISSILE, 3:DOUBLE, 4:LASER, 5:OPTION, 6:BARRIER
        self.gauge_labels = ["SPEED", "MISSILE", "DOUBLE", "LASER", "OPTION", "BARRIER"]
        self.speed_level = 3
        self.options = [] # オプションの数
        
        self.bullets = []
        self.items = [[600, 240]] # カプセルの初期位置
        self.running = True

    def update(self):
        keys = pygame.key.get_pressed()
        # 自機の移動
        if keys[pygame.K_UP]:    self.player_pos[1] -= self.speed_level
        if keys[pygame.K_DOWN]:  self.player_pos[1] += self.speed_level
        if keys[pygame.K_LEFT]:  self.player_pos[0] -= self.speed_level
        if keys[pygame.K_RIGHT]: self.player_pos[0] += self.speed_level

        # 座標履歴を更新（オプション用：20フレーム前の位置を追跡）
        self.history.appendleft(list(self.player_pos))

        # 弾の発射 (Shiftキー)
        for b in self.bullets:
            b[0] += 10
        self.bullets = [b for b in self.bullets if b[0] < SCREEN_WIDTH]

        # アイテム取得判定
        for item in self.items[:]:
            if abs(item[0] - self.player_pos[0]) < 20 and abs(item[1] - self.player_pos[1]) < 20:
                self.items.remove(item)
                self.power_gauge = (self.power_gauge % 6) + 1 # ゲージを進める

    def draw(self):
        self.screen.fill(BLACK)
        
        # オプションの描画 (自機の動きをトレース)
        for i in range(len(self.options)):
            delay = (i + 1) * 15 # 15フレーム間隔で追いかける
            if len(self.history) > delay:
                pos = self.history[delay]
                pygame.draw.circle(self.screen, RED, pos, 8)

        # 自機の描画
        pygame.draw.polygon(self.screen, WHITE, [[self.player_pos[0]+20, self.player_pos[1]], 
                                                 [self.player_pos[0]-10, self.player_pos[1]-10], 
                                                 [self.player_pos[0]-10, self.player_pos[1]+10]])
        
        # 弾とアイテムの描画
        for b in self.bullets: pygame.draw.rect(self.screen, YELLOW, (b[0], b[1], 10, 2))
        for item in self.items: pygame.draw.circle(self.screen, RED, item, 10)

        # パワーアップゲージの描画
        for i, label in enumerate(self.gauge_labels):
            color = BLUE if self.power_gauge == i + 1 else WHITE
            pygame.draw.rect(self.screen, color, (150 + i*100, 440, 90, 30), 2 if color == WHITE else 0)
            # テキスト表示（簡易版）
            font = pygame.font.SysFont(None, 24)
            img = font.render(label, True, WHITE if color == WHITE else BLACK)
            self.screen.blit(img, (155 + i*100, 445))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT: # 弾発射
                        self.bullets.append([self.player_pos[0], self.player_pos[1]])
                    if event.key == pygame.K_SPACE: # パワーアップ確定
                        if self.power_gauge == 1: self.speed_level += 1
                        if self.power_gauge == 5: self.options.append(True)
                        self.power_gauge = 0 # ゲージをリセット

            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()