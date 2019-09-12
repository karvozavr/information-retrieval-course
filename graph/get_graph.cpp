
#include "json.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;

using json = nlohmann::json;

static std::string base64_decode(const std::string &in) {

  std::string out;

  std::vector<int> T(256, -1);
  for (int i = 0; i < 64; i++) T["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[i]] = i;

  int val = 0, valb = -8;
  for (unsigned char c : in) {
    if (T[c] == -1) break;
    val = (val << 6) + T[c];
    valb += 6;
    if (valb >= 0) {
      out.push_back(char((val >> valb) & 0xFF));
      valb -= 8;
    }
  }
  return out;
}

size_t find_Nth(
  const std::string &str,   // where to work
  const std::string &find,    // what to 'find'
  unsigned N     // N'th ocurrence
) {
  if (0 == N) { return std::string::npos; }
  size_t pos, from = 0;
  unsigned i = 0;
  while (i < N) {
    pos = str.find(find, from);
    if (std::string::npos == pos) { break; }
    from = pos + 1; // from = pos + find.size();
    ++i;
  }
  return pos;
}

void build_graph(std::string const &dir) {
  std::ofstream out("g2.csv");
  for (auto &p: fs::directory_iterator(dir)) {
    std::ifstream in(p.path());
    json j;
    in >> j;
    std::string url = base64_decode(j["url"]);
    auto refs = j["references"];
    for (std::string ref : refs) {
      if (ref.rfind("http:", 0) == 0) {
        int pos1 = find_Nth(url, "/", 3);
        int pos2 = find_Nth(ref, "/", 3);

        url = url.substr(0, pos1 + 1);
        ref = ref.substr(0, pos2 + 1);

        out << '"' << url << "\",\"" << ref << "\"\n";
      }
    }
  }
}


int main(int argc, char **argv) {
  build_graph(argv[1]);
  return 0;
}
