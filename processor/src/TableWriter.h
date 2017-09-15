#pragma once

#include <initializer_list>
#include <fstream>

class TableWriter {
private:
  static const char CELL_SEPARATOR = '\t';
  static const char LINE_SEPARATOR = '\n';
public:
  TableWriter(std::fstream& out)
  : _out(out)
  , _atRowStart(true) {}

  template<typename T>
  void writeCell(T value) {
    beginCell();
    _out << value;
  }

  template<typename T>
  void writeCells(std::initializer_list<T> values) {
    for (const auto& value : values) {
      writeCell(value);
    }
  }

  template<typename Iter>
  void writeCells(Iter start, Iter end) {
    for (auto iter = start; iter != end; iter++) {
      writeCell(*iter);
    }
  }

  void writeBlankCell() {
    beginCell();
  }

  void writeBlankCells(std::size_t count) {
    for (auto i = 0; i < count; ++i) {
      writeBlankCell();
    }
  }

  void endRow() {
    _out << LINE_SEPARATOR;
    _atRowStart = true;
    _out.flush();
  }
private:
  void beginCell() {
    if (!_atRowStart) {
      _out << CELL_SEPARATOR;
    }
    _atRowStart = false;
  }

  std::fstream& _out;
  bool _atRowStart;
};
