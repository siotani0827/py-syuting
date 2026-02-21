import pygame
import random
import os
import math

# --- 設定 ---
WIDTH, HEIGHT = 800, 480
FPS = 60
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN  = (0, 255, 0)
PURPLE = (255, 0, 255)
CYAN   = (0, 255, 255)

PART_TYPES = [
    {"name": "CANNON", "color": YELLOW, "type": "straight"},
    {"name": "VULCAN", "color": CYAN,   "type": "spread"},
    {"name": "DRILL",  "color": RED,    "type": "heavy"}
]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Galaxy Shooter - Fast Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 25)
    big_font = pygame.font.SysFont("arial", 80)
    
    base_path = os.path.dirname(__file__)
    
    def load_img(name, size):
        path = os.path.join(base_path, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(surf, WHITE, (0, 0, size[0], size[1]), 1)
            return surf

    player_img = load_img("player.png", (40, 30))
    boss_img   = load_img("boss.png", (100, 100))
    enemy_img  = load_img("enemy.png", (30, 30))

    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random() * 3 + 1] for _ in range(70)]

    def reset_game():
        return {
            "px": 100, "py": 240, "speed": 5,
            "bullets": [], "scraps": [], "enemies": [], "boss_bullets": [],
            "parts": [], "enemy_count": 0, "boss": None, 
            "boss_max_hp": 100, "game_state": "TITLE", "is_paused": False, "frame_count": 0
        }

    g = reset_game()
    running = True

    while running:
        g["frame_count"] += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if g["game_state"] == "TITLE":
                    if event.key == pygame.K_z: g["game_state"] = "STAGE"
                elif g["game_state"] in ["GAMEOVER", "CLEAR"]:
                    if event.key == pygame.K_r: g = reset_game()
                else:
                    if event.key == pygame.K_LSHIFT: g["is_paused"] = not g["is_paused"]
                    if not g["is_paused"] and g["game_state"] in ["STAGE", "BOSS"]:
                        if event.key == pygame.K_z:
                            def add_bullet(x, y, vx, vy, color, pwr):
                                g["bullets"].append({"x": x, "y": y, "vx": vx, "vy": vy, "color": color, "power": pwr})
                            add_bullet(g["px"] + 20, g["py"], 12, 0, WHITE, 1)
                            for p in g["parts"]:
                                bx, by = g["px"] + p["offset"][0], g["py"] + p["offset"][1]
                                pt = p["type"]
                                if pt["name"] == "CANNON": add_bullet(bx+15, by, 18, 0, YELLOW, 1)
                                elif pt["name"] == "VULCAN":
                                    add_bullet(bx+15, by, 10, 2, CYAN, 1)
                                    add_bullet(bx+15, by, 10, -2, CYAN, 1)
                                elif pt["name"] == "DRILL": add_bullet(bx+15, by, 8, 0, RED, 3)

        if not g["is_paused"]:
            for s in stars:
                s[0] -= s[2]
                if s[0] < 0: s[0], s[1] = WIDTH, random.randint(0, HEIGHT)
        
        if not g["is_paused"] and g["game_state"] in ["STAGE", "BOSS"]:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and g["py"] > 20: g["py"] -= g["speed"]
            if keys[pygame.K_DOWN] and g["py"] < HEIGHT-20: g["py"] += g["speed"]
            if keys[pygame.K_LEFT] and g["px"] > 20: g["px"] -= g["speed"]
            if keys[pygame.K_RIGHT] and g["px"] < WIDTH-20: g["px"] += g["speed"]

            for b in g["bullets"]: b["x"] += b["vx"]; b["y"] += b["vy"]
            for bb in g["boss_bullets"]: bb[0] -= 7
            g["bullets"] = [b for b in g["bullets"] if -100 < b["x"] < WIDTH+100]

            targets = [{"x": g["px"], "y": g["py"], "is_main": True}]
            for i, p in enumerate(g["parts"]):
                targets.append({"x": g["px"] + p["offset"][0], "y": g["py"] + p["offset"][1], "is_main": False, "idx": i})
            hazards = [[e[0], e[1], "e", e] for e in g["enemies"]] + [[bb[0], bb[1], "b", bb] for bb in g["boss_bullets"]]
            
            for hz in hazards:
                for t in targets:
                    if math.hypot(hz[0]-t["x"], hz[1]-t["y"]) < 25:
                        if t["is_main"]: g["game_state"] = "GAMEOVER"
                        else:
                            if t["idx"] < len(g["parts"]): 
                                g["parts"].pop(t["idx"])
                                if hz[2] == "e" and hz[3] in g["enemies"]: g["enemies"].remove(hz[3])
                                elif hz[2] == "b" and hz[3] in g["boss_bullets"]: g["boss_bullets"].remove(hz[3])
                        break

            if g["game_state"] == "STAGE":
                # 出現頻度をわずかにアップ(0.07 -> 0.08)
                if random.random() < 0.08: g["enemies"].append([WIDTH, random.randint(50, HEIGHT-50)])
                if g["enemy_count"] >= 50:
                    g["game_state"] = "BOSS"
                    g["boss"] = [WIDTH-150, HEIGHT//2, g["boss_max_hp"], 1]

            for e in g["enemies"][:]:
                # --- 【修正】速度を 4 から 6 に変更 ---
                e[0] -= 6
                if e[0] < -30: g["enemies"].remove(e)
                for b in g["bullets"][:]:
                    hit_range = 35 if b["color"] == RED else 25
                    if math.hypot(e[0]-b["x"], e[1]-b["y"]) < hit_range:
                        if e in g["enemies"]: g["enemies"].remove(e)
                        g["enemy_count"] += 1
                        if b in g["bullets"]: g["bullets"].remove(b)
                        if random.random() < 0.4: g["scraps"].append({"x": e[0], "y": e[1], "type": random.choice(PART_TYPES)})

            if g["boss"]:
                g["boss"][1] += 3 * g["boss"][3]
                if g["boss"][1] < 50 or g["boss"][1] > HEIGHT-150: g["boss"][3] *= -1
                if random.random() < 0.08: g["boss_bullets"].append([g["boss"][0], g["boss"][1]+50])
                for b in g["bullets"][:]:
                    if g["boss"][0] < b["x"] < g["boss"][0]+100 and g["boss"][1] < b["y"] < g["boss"][1]+100:
                        g["boss"][2] -= b["power"]
                        if b in g["bullets"]: g["bullets"].remove(b)
                if g["boss"][2] <= 0: g["game_state"] = "CLEAR"

            for s in g["scraps"][:]:
                s["x"] -= 2
                if math.hypot(s["x"]-g["px"], s["y"]-g["py"]) < 40:
                    if len(g["parts"]) < 2:
                        ofs = [(0,-35), (0,35)]
                        g["parts"].append({"type": s["type"], "offset": ofs[len(g["parts"])]})
                    g["scraps"].remove(s)

        # --- 描画開始 ---
        screen.fill(BLACK)
        for s in stars: pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 1)
        
        if g["game_state"] == "TITLE":
            title_text = big_font.render("Galaxy Shooter", True, CYAN)
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 140))
            float_y = math.sin(g["frame_count"] * 0.05) * 15 
            screen.blit(pygame.transform.scale(player_img, (120, 90)), (WIDTH//2 - 60, HEIGHT//2 - 20 + float_y))
            if (g["frame_count"] // 30) % 2 == 0:
                st = font.render("PRESS Z TO START", True, WHITE)
                screen.blit(st, (WIDTH//2 - st.get_width()//2, HEIGHT//2 + 100))

        elif g["game_state"] in ["STAGE", "BOSS"]:
            for p in g["parts"]: pygame.draw.rect(screen, p["type"]["color"], (g["px"]+p["offset"][0]-10, g["py"]+p["offset"][1]-10, 20, 20))
            screen.blit(player_img, (g["px"]-20, g["py"]-15))
            
            for b in g["bullets"]:
                if b["color"] == YELLOW:
                    pygame.draw.rect(screen, YELLOW, (b["x"]-60, b["y"]-3, 60, 6))
                    pygame.draw.rect(screen, WHITE, (b["x"]-60, b["y"]-1, 60, 2))
                elif b["color"] == RED:
                    pygame.draw.rect(screen, RED, (b["x"], b["y"]-4, 18, 8))
                    pygame.draw.rect(screen, (255, 100, 100), (b["x"], b["y"]-1, 18, 2))
                else:
                    pygame.draw.rect(screen, b["color"], (b["x"], b["y"]-2, 12, 4))
            
            for e in g["enemies"]:
                screen.blit(enemy_img, (e[0]-15, e[1]-15))
            
            for s in g["scraps"]: pygame.draw.rect(screen, s["type"]["color"], (s["x"]-8, s["y"]-8, 16, 16), 2)
            
            if g["boss"]:
                screen.blit(boss_img, (g["boss"][0], g["boss"][1]))
                pygame.draw.rect(screen, RED, (g["boss"][0], g["boss"][1]-20, int(100*(g["boss"][2]/g["boss_max_hp"])), 10))
                pygame.draw.rect(screen, WHITE, (g["boss"][0], g["boss"][1]-20, 100, 10), 1)

            for bb in g["boss_bullets"]: pygame.draw.circle(screen, PURPLE, (bb[0], bb[1]), 8)
            
            screen.blit(font.render(f"PARTS: {len(g['parts'])}/2", True, WHITE), (10, 10))
            screen.blit(font.render(f"KILLS: {g['enemy_count']}", True, WHITE), (10, 40))

        elif g["game_state"] == "GAMEOVER":
            go_text = big_font.render("GAME OVER", True, RED)
            screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
            rst_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(rst_text, (WIDTH//2 - rst_text.get_width()//2, HEIGHT//2 + 50))

        elif g["game_state"] == "CLEAR":
            screen.blit(big_font.render("MISSION COMPLETE", True, YELLOW), (WIDTH//2-300, HEIGHT//2-50))
            screen.blit(font.render("Press R to Title", True, WHITE), (WIDTH//2-80, HEIGHT//2+50))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()