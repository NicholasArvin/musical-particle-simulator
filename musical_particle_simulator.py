import pygame
import random
import librosa
import imageio


# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Pygame window dimensions
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Musical Particle Simulation')

video_writer = imageio.get_writer('animation.mp4', fps=60)


# Particle class
class Particle:
    def __init__(self):
        self.shape = 'circle'
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.1, 1.0)
        self.direction = random.uniform(0, 2 * 3.1416)
        # self.colors = [(255, 50, 100), (33, 33, 100), (200, 200, 50)]  # Define a set of colors
        # self.color_index = 0  # Index to track the current color in the set
        # self.color = self.colors[self.color_index]  # Initialize particle color
        self.color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        self.size = random.randint(2, 6)  # Initialize particle size
        self.min_size = 2  # Minimum size for particles
        self.mid_size = 10
        self.max_size = 35  # Maximum size for particles when loud
        self.min_loudness = 0.07  # Minimum loudness threshold
        self.mid_loudness = 0.18  # Medium loudness threshold
        self.max_loudness = 0.22  # Maximum loudness threshold
        self.ultra_max_loudness = .24
        self.velocity_x = random.uniform(-1, 1)  # Initial velocity components
        self.velocity_y = random.uniform(-1, 1)
        self.acceleration = 0.08  # Initial acceleration factor
        self.acceleration_multiplier = 1.0  # Multiplier for acceleration adjustments

    def move(self, beat, loudness):
        if beat:  # Change size on beat
            if self.min_loudness <= loudness < self.mid_loudness:
                self.size = random.randint(self.min_size, self.mid_size)
            else:
                self.size = random.randint(self.min_size, self.max_size)
                if self.shape == 'triangle':
                    self.shape = 'circle'

        if loudness >= self.max_loudness and random.random() < 0.2:  #  condition with 20% chance
            self.shape = 'triangle'

        # print(loudness)
        # Adjust particle color and size based on loudness
        if loudness < self.min_loudness:
            self.color = (random.choice([(173, 216, 230), (255, 192, 203)]))  # Light blue, pink
            # self.size = min(self.size, self.max_size)  # Ensure size doesn't exceed max size 

        elif self.min_loudness <= loudness < self.mid_loudness:
            self.color = (random.choice([(255, 192, 203),(255, 255, 0) ]))  # pink, yellow
            # self.size = min(self.size + 2, self.max_size)  # Increase size gradually

        elif self.mid_loudness <= loudness < self.max_loudness:
             self.color = (random.choice([(255, 255,0),(255, 165, 0), ]))  # yellow, orange
            #  self.size = min(self.size + 4, self.max_size)  # Increase size faster

        elif self.max_loudness <= loudness < self.ultra_max_loudness:
            self.color = (random.choice([(255, 165,0),(255, 0, 0), ]))  # Orange
            # self.size = min(self.size + 6, self.max_size)  # Increase size rapidly

        else:
            self.color = (255, 0, 0)  # Red
            # self.size = min(self.size + 6, self.max_size)  # Increase size rapidly
            
        # Adjust acceleration based on silence duration and loudness
        if loudness < self.min_loudness:  # Silence detected
            if self.acceleration_multiplier > 0.1:  # Limit minimum acceleration multiplier
                self.acceleration_multiplier -= 0.02  # Reduce acceleration over time

        elif loudness >= self.max_loudness:  # Loudness threshold exceeded
            if self.acceleration_multiplier < 1.0:  # Limit maximum acceleration multiplier
                self.acceleration_multiplier += 0.02  # Increase acceleration over time

        self.velocity_x += random.uniform(-self.acceleration * self.acceleration_multiplier,
                                          self.acceleration * self.acceleration_multiplier)
        self.velocity_y += random.uniform(-self.acceleration * self.acceleration_multiplier,
                                          self.acceleration * self.acceleration_multiplier)

        # Update particle position based on velocity
        self.x += self.speed * self.velocity_x
        self.y += self.speed * self.velocity_y

        # Keep particles within the screen
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self):
        if self.shape == 'circle':
            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.size)
        elif self.shape == 'triangle':
            # Draw a triangle instead of a circle when the shape is set to 'triangle'
            triangle_points = [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ]
            pygame.draw.polygon(window, self.color, triangle_points)

# Load audio file and get audio data
# put whatever audio file you want here
audio_file = 'sparta.mp3'  # Replace with your audio file

# pygame.mixer.music.play()

# Calculate tempo and beat times
y, sr = librosa.load(audio_file)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
loudness = librosa.feature.rms(y=y)

# Create particles
particles = [Particle() for _ in range(200)]

# Main loop
running = True


current_beat_time_index = 0
time_passed = 0

pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()
clock = pygame.time.Clock()
frames = []  # Store frames
while running:
    window.fill((0, 0, 0))  # Clear the window

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.mixer.music.get_pos() / 1000  # Get current time in seconds

    # Check if the current time matches any beat times
    # print(current_time,beat_times[current_beat_time_index],abs(current_time - beat_times[current_beat_time_index]))
    if current_beat_time_index < len(beat_times) and abs(current_time - beat_times[current_beat_time_index]) < 0.05:
        # If the current time matches a beat time (with a tolerance of 0.1 seconds), trigger color change for particles
        # print('here')
        for particle in particles:
            particle.move(True,loudness[0][60*int(current_time)])  # Trigger color change on beat
            particle.draw()
        current_beat_time_index += 1  # Move to the next beat time
    else:
        # Move and draw particles
        for particle in particles:
            particle.move(False,loudness[0][60*int(current_time)])  # Particle movement not affected by beat in this version
            particle.draw()

    pygame.display.update()

    surface_data = pygame.surfarray.array3d(window)
    frames.append(surface_data)
    if current_beat_time_index == 200:
        imageio.mimwrite('animation.mp4', frames, fps=60)
    clock.tick(60)  # Limit frame rate to 60 FPS


pygame.quit()
