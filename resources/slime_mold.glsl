#version 430

// this defines the local size of the shader, i.e. the size of a single work group
// the number of work groups is defined externally (python in my case)

// in this shader, we are not separating the work based on image segments, but instead based on agents
// therefore, we only use one dimension of local_size
layout (local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

// the trail map is an image bound at location 0
layout (rgba8, location = 0) uniform image2D trailMap;

struct Agent {
    vec2 pos;
    vec2 dir;
};

layout (std140, binding = 0) buffer buf_ants {
    Agent agents[];
} Buf_agents;

uniform uint width;
uniform uint height;
uniform uint n_agents;
uniform float speed;
uniform float steerStrength;
uniform float sensorAngleSpacing;
uniform int sensorSize;
uniform int sensorDistance;

// time is used for pseudo-random number generation
uniform uint timer;


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

void main() {
    // agent index is the global invocation id
    const uint id = gl_GlobalInvocationID.x;

    Agent agent = Buf_agents.agents[id];

    vec2 newPos = agent.pos + agent.dir * speed;
    vec2 newDir = agent.dir;

    // check if agent is out of map and adjust direction
    if (newPos.x < 0 || newPos.x > width) {
        newPos.x = clamp(newPos.x, 0.1, width - 0.1);
        newDir.x *= -1;
    }

    if (newPos.y < 0 || newPos.y > height) {
        newPos.y = clamp(newPos.y, 0.1, height - 0.1);
        newDir.y *= -1;
    }

    // update Agent buffer with the new position and direction
    Buf_agents.agents[id].pos = newPos;
    Buf_agents.agents[id].dir = newDir;

    ivec2 texelPos = ivec2(agent.pos);
    const vec4 texel = vec4(1.0);
    
    imageStore(trailMap, texelPos, texel);
}
