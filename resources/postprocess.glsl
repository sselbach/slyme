#version 430

layout (local_size_x = 16, local_size_y = 16) in;

layout (rgba8, location = 0) uniform restrict image2D trailMap;

uniform uint width;
uniform uint height;

uniform float diffusionStrength;
uniform bool evaporateExponentially;
uniform float evaporationStrength;
uniform float minimalAmount;


void main() {
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);
    float texel = imageLoad(trailMap, texelPos).r;

    if (texelPos.x >= width || texelPos.y >= height) 
        return;

    // STEP 1: Blurring using box filter, might replace with Gaussian filter later
    float blur = 0.0;

    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            int x = texelPos.x + dx;
            int y = texelPos.y + dy;

            if (x >= 0 && x < width && y >= 0 && y < height) {
                blur += imageLoad(trailMap, ivec2(x, y)).r;
            }
        }
    }

    blur /= 9.0;

    float diffused = mix(texel, blur, diffusionStrength);

    // STEP 2: Evaporate using either exponential or linear decay
    
    if (evaporateExponentially) {
        diffused *= 1.0 - evaporationStrength;
        diffused = max(minimalAmount, diffused);            
    } else {
        diffused = max(0, diffused - evaporationStrength);
    }


    imageStore(trailMap, texelPos, vec4(diffused, diffused, diffused, 1.0));
}