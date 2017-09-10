#include "Settings.h"

std::string formatToString(OutputFormat value) {
  switch (value) {
    case OutputFormat::JSON:
      return "json";
    default:
      return "unknown";
  }
}
