/* ISF Shader Example
   name: Example Wave Shader
   description: A simple animated wave pattern
   author: ISF Shader Renderer
   version: 1.0
*/

uniform float TIME;
uniform vec2 RENDERSIZE;

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    
    // Create a wave pattern that animates over time
    float wave = sin(uv.x * 10.0 + TIME * 2.0) * 0.5 + 0.5;
    wave *= sin(uv.y * 8.0 + TIME * 1.5) * 0.5 + 0.5;
    
    // Add some color variation
    vec3 color = vec3(
        wave * 0.8 + 0.2,
        wave * 0.6 + 0.4,
        wave * 0.9 + 0.1
    );
    
    // Add a gradient overlay
    color *= 1.0 - uv.y * 0.3;
    
    gl_FragColor = vec4(color, 1.0);
} 