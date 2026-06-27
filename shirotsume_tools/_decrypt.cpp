#include <cstddef>
#include <cstring>

#include <string>
#include <iostream>
#include <fstream>
#ifdef _WIN32
#include <direct.h>
#else
#include <unistd.h>
#endif
#include "decrypt.h"

void decrypt(uint8_t *buf, size_t size, uint32_t key) {
  std::size_t i;

  uint32_t *h = (uint32_t *)buf;
  for (i = 0; i < (size >> 2); i++) {
    uint32_t txt = h[i] ^ key;
    h[i] = txt;
    key += ((txt << 16) | (txt >> 16)) ^ 0x98fcdba2;
  }
}

void file_decrypt(uint8_t *buf, size_t size) {
  std::size_t i;

  uint32_t *h = (uint32_t *)buf;
  for (i = 0; i < (size >> 2); i++) {
    h[i] = (h[i] << 6) ^ ((h[i] << 6) ^ ((h[i] ^ 0x9b9b9b9b) >> 2)) & 0x3f3f3f3f;
  }
}

void decomp(uint8_t *comp_buf, uint8_t *buf, size_t size) {
  std::size_t decomp_size;

  uint8_t cache[0x1000];
  uint16_t cache_ptr;

  uint8_t read_mask, mask;  

  decomp_size = 0;

  memset(cache, 0, 0x1000);
  cache_ptr = 0xfee;

  read_mask = 0;
  mask = 0;

  for (;;) {
    if (read_mask == 0) {
      read_mask = 0xff;
      mask = *comp_buf;
      comp_buf++;
    }
    if (mask & 1) {
      *buf = *comp_buf;
      cache[cache_ptr] = *comp_buf;

      buf++;
      comp_buf++;
      decomp_size++;

      cache_ptr++;
      cache_ptr &= 0xfff;

      if (decomp_size == size) {
        return;
      }
    } else {
      uint8_t byte_0, byte_1;

      byte_0 = *comp_buf;
      comp_buf++;
      byte_1 = *comp_buf;
      comp_buf++;

      uint16_t offset = ((byte_1 & 0xf0) << 4) | byte_0;
      uint8_t length = (byte_1 & 0x0f) + 3;

      for (uint8_t i = 0; i < length; i++) {
        *buf = cache[(offset + i) & 0xfff];
        cache[cache_ptr] = *buf;

        buf++;
        decomp_size++;

        cache_ptr++;
        cache_ptr &= 0xfff;

        if (decomp_size == size) {
          return;
        }
      }    
    }

    read_mask >>= 1;
    mask >>= 1;
  }
}

#ifdef DECRYPT_MAIN
int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <path> [-o/--output <outdir>]" << std::endl;
    return 1;
  }

  ::std::string path = argv[1];
  if (path.size() < 4 || path.rfind(".dat") != path.size() - 4) {
    std::cerr << "the suffix of pack file should be .dat" << std::endl;
    return 1;
  }
  ::std::string outdir;

  for (int i = 2; i < argc; i++) {
    if (!strcmp(argv[i], "-o") && i + 1 < argc) {
      i++;
      outdir = argv[i];
    }
  }

  if (outdir.empty()) {
    outdir = path.substr(0, path.size() - 4);
  }

  std::cout << "input: " << path << std::endl;
  std::cout << "output: " << outdir << std::endl;

  std::ifstream pack{path, std::ios::in | std::ios::binary};

  if (!pack.is_open()) {
    std::cerr << "cannot open file: " << strerror(errno) << std::endl;
    return 1;
  }

  char sig[8];
  pack.read(sig, 8);
  if (memcmp(sig, "RepiPack", 8)) {
    std::cerr << "invalid file head" << std::endl;
    return 1;
  }

  // small endian
  uint32_t version;
  pack.read((char *)&version, 4);
  if (version != 2) {
    std::cerr << "invalid version" << std::endl;
    return 1;
  }

  uint32_t header_size;
  pack.read((char *)&header_size, 4);

  char *header = new char[header_size];
  pack.read(header, header_size);

  decrypt((uint8_t *)header, header_size, 0x837fc07a);

  delete [] header;

  uint32_t file_count;
  pack.read((char *)&file_count, 4);

  file_header_t *file_header_list = new file_header_t[file_count];
  
  for (std::size_t i = 0; i < file_count; i++) {
    char buf[80];
    file_header_t *p = file_header_list + i;

    pack.read(buf, 80);
    decrypt((uint8_t *)buf, 80, 0xf517aa26);

    strcpy(p->name, buf);
    p->offset = *(uint32_t *)(buf + 64);
    p->size = *(uint32_t *)(buf + 68);
    p->comp_size = *(uint32_t *)(buf + 72);
    p->crypt_type = buf[76];
  }

  _mkdir(outdir.c_str());

  for (std::size_t i = 0; i < file_count; i++) {
    file_header_t *p = file_header_list + i;

    std::ofstream file{
      outdir + '/' + p->name,
      std::ios::out | std::ios::binary
    };

    if (!file.is_open()) {
      std::cerr << "cannot open file" << outdir << '/' << p->name << ": " << strerror(errno) << std::endl;
      return 1;
    }

    uint8_t *buf = new uint8_t[p->comp_size];

    pack.seekg(p->offset, std::ios::beg);
    pack.read((char *)buf, p->comp_size);

    if (p->crypt_type == 1) {
      decrypt(buf, p->comp_size, 0xf517aa26);
    } else if (p->crypt_type == 2) {
      file_decrypt(buf, p->comp_size);
    }

    if (p->comp_size != p->size) {
      uint8_t *comp_buf = buf;
      buf = new uint8_t[p->size];
      decomp(comp_buf, buf, p->size);
      delete [] comp_buf;
    }

    file.write((char *)buf, p->size);

    delete [] buf;
  }

  delete [] file_header_list;
  return 0;

fail:
  return 1;
}
#endif
