#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct file_header {
    char name[0x40];
    uint32_t offset;
    uint32_t size;
    uint32_t comp_size;
    uint8_t  crypt_type;
} file_header_t;

void decrypt(uint8_t *buf, size_t size, uint32_t key);
void file_decrypt(uint8_t *buf, size_t size);
void decomp(uint8_t *comp_buf, uint8_t *buf, size_t size);

#ifdef __cplusplus
}
#endif