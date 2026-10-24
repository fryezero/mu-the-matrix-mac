/* SPDX-License-Identifier: MIT
 * Offline synthetic renderer stress test. No game, account, network or hooks.
 * glcrowd.exe frames batches vertices scene probes [width height [buffers]]
 * scene: 0 mixed, 1 crosses view edge, 2 offscreen, 3 inside; probes: 0 old, 1 new.
 * Reports unpaced work including GPU completion and swap, not game FPS.
 */
#include <windows.h>
#include <GL/gl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../hotpatch/cull_geometry.h"

static LRESULT CALLBACK window_proc(HWND w, UINT m, WPARAM a, LPARAM b) { return DefWindowProcA(w, m, a, b); }
static int number(const char *s, int low, int high) {
    char *end; long n = strtol(s, &end, 10);
    if (!*s || *end || n < low || n > high) return -1;
    return (int)n;
}
static int compare_double(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y);
}
static unsigned framebuffer_hash(int width, int height) {
    size_t n = (size_t)width * height * 4;
    unsigned char *pixels = malloc(n); unsigned h = 2166136261u;
    if (!pixels) return 0;
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
    for (size_t i = 0; i < n; i++) h = (h ^ pixels[i]) * 16777619u;
    free(pixels); return h;
}
int main(int argc, char **argv) {
    if (argc != 6 && argc != 8 && argc != 9) { fprintf(stderr, "glcrowd frames batches vertices scene probes [width height [buffers]]\n"); return 2; }
    int frames = number(argv[1], 5, 300), batches = number(argv[2], 1, 50000), vertices = number(argv[3], 3, 6000);
    int scene = number(argv[4], 0, 3), probes = number(argv[5], 0, 1);
    int width = argc >= 8 ? number(argv[6], 64, 2048) : 640;
    int height = argc >= 8 ? number(argv[7], 64, 2048) : 480;
    int buffers = argc == 9 ? number(argv[8], 0, 4096) : 0;
    if (frames < 0 || batches < 0 || vertices < 0 || vertices % 3 || scene < 0 || probes < 0 || width < 0 || height < 0 || buffers < 0) return 2;
    WNDCLASSA wc = {0}; wc.lpfnWndProc = window_proc; wc.hInstance = GetModuleHandleA(NULL); wc.lpszClassName = "mu-crowd";
    if (!RegisterClassA(&wc)) return 2;
    RECT rect = {0, 0, width, height}; AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);
    HWND w = CreateWindowA(wc.lpszClassName, "Synthetic Wine rendering stress", WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                          0, 0, rect.right - rect.left, rect.bottom - rect.top, NULL, NULL, wc.hInstance, NULL);
    if (!w) return 2;
    HDC dc = GetDC(w);
    PIXELFORMATDESCRIPTOR pfd = {0};
    pfd.nSize = sizeof(pfd); pfd.nVersion = 1; pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
    pfd.iPixelType = PFD_TYPE_RGBA; pfd.cColorBits = 32;
    pfd.cDepthBits = 24;
    int fmt = ChoosePixelFormat(dc, &pfd);
    if (!fmt || !SetPixelFormat(dc, fmt, &pfd)) return 2;
    HGLRC rc = wglCreateContext(dc);
    if (!rc || !wglMakeCurrent(dc, rc)) return 2;
    typedef BOOL (WINAPI *SwapInterval)(int);
    PROC function = wglGetProcAddress("wglSwapIntervalEXT");
    SwapInterval interval = NULL; memcpy(&interval, &function, sizeof(interval));
    int no_vsync = interval && interval(0);
    fprintf(stderr, "GL vendor=%s renderer=%s version=%s swap_interval_zero=%d\n", glGetString(GL_VENDOR), glGetString(GL_RENDERER), glGetString(GL_VERSION), no_vsync);
    glViewport(0, 0, width, height); glDisable(GL_DITHER);
    glClearColor(.06f, .09f, .12f, 1); glEnable(GL_DEPTH_TEST); glDepthFunc(GL_LEQUAL);
    glEnable(GL_TEXTURE_2D); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    GLuint textures[8]; glGenTextures(8, textures);
    for (int t = 0; t < 8; t++) {
        unsigned char image[16 * 16 * 4];
        for (int i = 0; i < 16 * 16; i++) {
            image[4*i] = (unsigned char)(80 + t*20); image[4*i+1] = (unsigned char)(i % 16 * 15);
            image[4*i+2] = 160; image[4*i+3] = (unsigned char)(100 + i % 100);
        }
        glBindTexture(GL_TEXTURE_2D, textures[t]);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 16, 16, 0, GL_RGBA, GL_UNSIGNED_BYTE, image);
    }
    MuglCullVertex *source = calloc((size_t)64 * vertices, sizeof(*source));
    MuglCullVertex *batch = malloc((size_t)vertices * sizeof(*batch));
    if (!source || !batch) return 2;
    for (int b = 0; b < 64; b++) for (int j = 0; j < vertices; j++) {
        MuglCullVertex *v = source + b * vertices + j;
        int off = scene == 2 || (scene == 0 && b % 2);
        v->t[0] = (j % 16) / 15.f; v->t[1] = (j % 7) / 6.f;
        v->c[0] = .4f + (j % 3) * .2f; v->c[1] = .5f; v->c[2] = .8f; v->c[3] = .7f; v->n[2] = 1;
        float dx = j % 3 == 1 ? .01f : 0;
        v->v[0] = off ? 2.0f + dx : scene == 3 ? .2f + dx : j == 0 ? 1.02f : .96f + dx;
        v->v[1] = -.95f + b * .029f + (j % 3 == 2 ? .01f : 0) + (j / 3 % 20) * .002f; v->v[2] = (j / 3 % 20) * .001f;
    }
    const double matrix[16] = {1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
    typedef void (WINAPI *GenBuffers)(GLsizei, GLuint *);
    typedef void (WINAPI *BindBuffer)(GLenum, GLuint);
    typedef void (WINAPI *BufferData)(GLenum, ptrdiff_t, const void *, GLenum);
    typedef void (WINAPI *BufferSubData)(GLenum, ptrdiff_t, ptrdiff_t, const void *);
    typedef void (WINAPI *GetBufferData)(GLenum, ptrdiff_t, ptrdiff_t, void *);
    typedef void (WINAPI *GetBufferParameter)(GLenum, GLenum, GLint *);
    GenBuffers gen_buffers = NULL, delete_buffers = NULL;
    BindBuffer bind_buffer = NULL; BufferData buffer_data = NULL; BufferSubData buffer_sub_data = NULL;
    GetBufferData get_buffer_data = NULL; GetBufferParameter get_buffer_parameter = NULL;
    GLuint *ids = NULL;
    if (buffers) {
#define LOAD_BUFFER_FN(target, name) do { PROC p = wglGetProcAddress(name); memcpy(&target, &p, sizeof(target)); } while (0)
        LOAD_BUFFER_FN(gen_buffers, "glGenBuffersARB"); LOAD_BUFFER_FN(bind_buffer, "glBindBufferARB");
        LOAD_BUFFER_FN(buffer_data, "glBufferDataARB"); LOAD_BUFFER_FN(buffer_sub_data, "glBufferSubDataARB");
        LOAD_BUFFER_FN(delete_buffers, "glDeleteBuffersARB");
        LOAD_BUFFER_FN(get_buffer_data, "glGetBufferSubDataARB");
        LOAD_BUFFER_FN(get_buffer_parameter, "glGetBufferParameterivARB");
#undef LOAD_BUFFER_FN
        if (!gen_buffers || !bind_buffer || !buffer_data || !buffer_sub_data || !delete_buffers || !get_buffer_data || !get_buffer_parameter) return 2;
        ids = calloc(buffers, sizeof(*ids)); if (!ids) return 2;
        gen_buffers(buffers, ids);
        for (int i = 0; i < buffers; i++) {
            bind_buffer(0x8892, ids[i]);
            buffer_data(0x8892, (ptrdiff_t)((size_t)vertices * sizeof(*batch)), source + (i % 64) * vertices, 0x88e8);
        }
        bind_buffer(0x8892, 0);
    }
    glInterleavedArrays(GL_T2F_C4F_N3F_V3F, sizeof(*batch), batch);
    LARGE_INTEGER frequency, a, b, c, d; QueryPerformanceFrequency(&frequency);
    double times[300], sum = 0; unsigned hash = 0; unsigned long long culled = 0, drawn = 0; int late = 0;
    for (int frame = 0; frame < frames + 8; frame++) {
        MSG msg; while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) { TranslateMessage(&msg); DispatchMessageA(&msg); }
        QueryPerformanceCounter(&a); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        for (int k = 0; k < batches; k++) {
            memcpy(batch, source + (k % 64) * vertices, (size_t)vertices * sizeof(*batch));
            batch[0].v[1] += (frame % 5) * .001f; /* deterministic animated input */
            if (mugl_cull_geometry(matrix, batch, vertices, probes)) { if (frame >= 8) culled++; continue; }
            if (frame >= 8) drawn++;
            if (buffers) {
                bind_buffer(0x8892, ids[k % buffers]);
                buffer_sub_data(0x8892, 0, (ptrdiff_t)((size_t)vertices * sizeof(*batch)), batch);
                glInterleavedArrays(GL_T2F_C4F_N3F_V3F, sizeof(*batch), NULL);
            }
            glBindTexture(GL_TEXTURE_2D, textures[k % 8]);
            if (k % 4 == 0) glEnable(GL_BLEND); else if (k % 4 == 1) glDisable(GL_BLEND);
            glDrawArrays(GL_TRIANGLES, 0, vertices);
        }
        glFinish(); QueryPerformanceCounter(&b);
        if (frame == frames + 7) hash = framebuffer_hash(width, height); /* exclude readback from timing */
        QueryPerformanceCounter(&c);
        if (!SwapBuffers(dc)) return 2;
        QueryPerformanceCounter(&d);
        if (frame >= 8) {
            double ms = ((b.QuadPart - a.QuadPart) + (d.QuadPart - c.QuadPart)) * 1000.0 / frequency.QuadPart;
            times[frame - 8] = ms; sum += ms; if (ms > 40) late++;
        }
    }
    int lifecycle_ok = 1;
    if (buffers) {
        /* Outside timing: deleted/reused names must still resolve to correct rows. */
        for (int i = 0; i < 3; i++) {
            GLuint id = ids[i == 0 ? 0 : i == 1 ? buffers / 2 : buffers - 1];
            unsigned input[4] = {17, 23, (unsigned)i, 0xabcdef}, output[4] = {0}; GLint size = 0;
            delete_buffers(1, &id); bind_buffer(0x8892, id);
            buffer_data(0x8892, sizeof(input), input, 0x88e8);
            unsigned changed = 101; input[1] = changed;
            buffer_sub_data(0x8892, sizeof(unsigned), sizeof(unsigned), &changed);
            get_buffer_parameter(0x8892, 0x8764, &size);
            get_buffer_data(0x8892, 0, sizeof(output), output);
            if (size != sizeof(input) || memcmp(input, output, sizeof(input))) lifecycle_ok = 0;
        }
        bind_buffer(0x8892, 0); delete_buffers(buffers, ids); free(ids);
    }
    GLenum error = glGetError(); qsort(times, frames, sizeof(*times), compare_double);
    printf("{\"frames\":%d,\"batches\":%d,\"vertices\":%d,\"scene\":%d,\"probes\":%d,\"width\":%d,\"height\":%d,\"buffers\":%d,\"buffer_lifecycle_ok\":%d,"
           "\"mean_ms\":%.4f,\"median_ms\":%.4f,\"p95_ms\":%.4f,\"p99_ms\":%.4f,\"over_40ms\":%d,"
           "\"drawn\":%llu,\"culled\":%llu,\"framebuffer_hash\":\"%08x\",\"gl_error\":%u}\n",
           frames,batches,vertices,scene,probes,width,height,buffers,lifecycle_ok,sum/frames,times[(frames-1)/2],times[(frames*95+99)/100-1],times[(frames*99+99)/100-1],late,drawn,culled,hash,error);
    free(source); free(batch); glDeleteTextures(8, textures); wglMakeCurrent(NULL, NULL); wglDeleteContext(rc);
    ReleaseDC(w, dc); DestroyWindow(w);
    return error || !lifecycle_ok ? 2 : 0;
}
