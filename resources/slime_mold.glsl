#version 430
#define PI 3.1415926535897932384626

// this defines the local size of the shader, i.e. the size of a single work group
// the number of work groups is defined externally (python in my case)

// in this shader, we are not separating the work based on image segments, but instead based on agents
// therefore, we only use one dimension of local_size
layout (local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

// the trail map is an image bound at location 0
layout (rgba8, location = 0) uniform restrict image2D trailMap;

struct Agent {
    vec2 pos;
    vec2 dir;
};

layout (std140, binding = 0) restrict buffer buf_ants {
    Agent agents[];
} Buf_agents;

uniform uint width;
uniform uint height;
uniform uint n_agents;
uniform float speed;
uniform float sensorAngle;
uniform int sensorSize;
uniform float sensorDistance;
uniform float rotationAngle;
uniform float randomNoiseStrength;
uniform float noiseBias;

// time is used for pseudo-random number generation
uniform uint time;


uint hash(uint state) {
    state ^= 2747636419u;
    state *= 2654435769u;
    state ^= state >> 16u;
    state *= 2654435769u;
    state ^= state >> 16u;
    state *= 2654435769u;
    return state;
}

const float maxPossibleHash = 4294967295.0;
uint RNGState;

float random() {
    RNGState = hash(RNGState);

    return float(RNGState) / maxPossibleHash;
}

float sense(Agent agent, float sensorAngleOffset) {
    float angle = atan(agent.dir.y, agent.dir.x);

    float sensorAngle = angle + sensorAngleOffset;
    vec2 sensorDir = vec2(cos(sensorAngle), sin(sensorAngle));

    ivec2 sensorCenter = ivec2(agent.pos + sensorDir * sensorDistance);

    int halfSize = sensorSize / 2;
    int oddSize = sensorSize % 2;

    float sum = 0.0;

    for (int dy = -halfSize; dy < (halfSize + oddSize); dy++) {
        for (int dx = -halfSize; dx < (halfSize + oddSize); dx++) {
            int x = sensorCenter.x + dx;
            int y = sensorCenter.y + dy;

            if (x >= 0 && x < width && y >= 0 && y < height) {
                sum += imageLoad(trailMap, ivec2(x, y)).r;
            }
        }
    }

    return sum;
}

vec2 turn(vec2 dir, float angle) {
    const float newX = dir.x * cos(angle) - dir.y * sin(angle);
	const float newY = dir.x * sin(angle) + dir.y * cos(angle);
	return vec2(newX, newY);
}

vec2 random_direction() {
    const float angle = random() * 2.0 * PI;
    const float x = cos(angle);
    const float y = sin(angle);

    return vec2(x, y);
}

void main() {
    // agent index is the global invocation id
    const uint id = gl_GlobalInvocationID.x;

    if (id >= n_agents) 
        return;

    // initialize RNG state with id and current time (should be unique)
    RNGState = time * n_agents + id;

    Agent agent = Buf_agents.agents[id];

    vec2 newDir = agent.dir;

    // measure pheromone level at all three sensors
    float weightForward = sense(agent, 0.0);
    float weightLeft = sense(agent, sensorAngle);
    float weightRight = sense(agent, -sensorAngle);

    // choose steering direction based on results
    if (weightForward > weightLeft && weightForward > weightRight) {
        // do nothing
    } 
    else if (weightForward < weightLeft && weightForward < weightRight) {
        // if forward is less then both, randomly choose wether to turn left or right
        newDir = turn(agent.dir, ((random() < 0.5) ? rotationAngle : -rotationAngle));
    }
    else if (weightRight < weightLeft) {
        // turn left
        newDir = turn(agent.dir, rotationAngle);
    }
    else if (weightLeft < weightRight) {
        // turn right
        newDir = turn(agent.dir, -rotationAngle);
    }

    // add random noise to direction
    float noise = random() * randomNoiseStrength;

    noise = noise - (0.5 - 0.5 * noiseBias) * randomNoiseStrength;

    newDir = turn(newDir, noise);

    vec2 newPos = agent.pos + newDir * speed;



    // check if agent is out of map and adjust direction
    if (newPos.x < 0 || newPos.x > width) {
        newPos.x = clamp(newPos.x, 0.1, float(width) - 0.1);
        newDir.x *= -1;
    }

    if (newPos.y < 0 || newPos.y > height) {
        newPos.y = clamp(newPos.y, 0.1, float(height) - 0.1);
        newDir.y *= -1;
    }

    // update Agent buffer with the new position and direction
    Buf_agents.agents[id].pos = newPos;
    Buf_agents.agents[id].dir = newDir;

    ivec2 texelPos = ivec2(agent.pos);
    const vec4 texel = vec4(1.0, 1.0, 1.0, 1.0);
    
    imageStore(trailMap, texelPos, texel);
}
