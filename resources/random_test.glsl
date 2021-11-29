#version 430

// this defines the local size of the shader, i.e. the size of a single work group
// the number of work groups is defined externally (python in my case)
layout (local_size_x = 32, local_size_y = 32) in;


// match the input texture format!
layout (rgba8, location = 0) writeonly uniform image2D destTex;
uniform float time;

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
    uint width = 1920;

    // convert to 1D index
    uint pixelIndex = texelPos.y * width + texelPos.x;
    uint pseudoRandomNumber = hash(pixelIndex * int(time * 144));

    float maxPossibleHash = 4294967295.0;
    float normalized = pseudoRandomNumber / maxPossibleHash;


    imageStore(
        destTex,
        texelPos,
        vec4(
            normalized,
            normalized,
            normalized,
            1.0
        )
    );
}
