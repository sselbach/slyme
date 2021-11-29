#version 430

// this defines the local size of the shader, i.e. the size of a single work group
// the number of work groups is defined externally (python in my case)

// in this shader, we are not separating the work based on image segments, but instead based on agents
// therefore, we only use one dimension of local_size
layout (local_size_x = 16, local_size_y = 1, local_size_z = 1) in;

// match the input texture format!
layout (rgba8, location = 0) uniform image2D trailMap;

uniform float time;
uniform uint width;
uniform uint height;

struct Agent {
    vec2 pos;
    vec2 dir;
};

layout (std430, binding = 0) buffer buf_ants {
    Agent agents[];
} Buf_agents;

uniform uint n_agents;

// hash function for psuedo random number generation
uint hash(uint state) {
    state ^= 2747636419;
    state *= 2654435769;
    state ^= state >> 16;
    state *= 2654435769;
    state ^= state >> 16;
    state *= 2654435769;
    return state;
}

void main() {
    // texel coordinate we are writing to
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);

    // convert to 1D index
    uint pixelIndex = texelPos.y * width + texelPos.x;
    uint pseudoRandomNumber = hash(pixelIndex * int(time * 144));

    float maxPossibleHash = 4294967295.0;
    float normalized = pseudoRandomNumber / maxPossibleHash;


    imageStore(
        trailMap,
        texelPos,
        vec4(
            normalized,
            normalized,
            normalized,
            1.0
        )
    );
}
