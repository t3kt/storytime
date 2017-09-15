#pragma once

#include <initializer_list>
#include <fstream>
#include <ofMain.h>

class TableWriter {
private:
  static const char CELL_SEPARATOR = '\t';
  static const char LINE_SEPARATOR = '\n';
public:
  TableWriter(std::fstream& out)
  : _out(out)
  , _atRowStart(true) {}

  template<typename T>
  TableWriter& writeCell(T value) {
    beginCell();
    _out << value;
    return *this;
  }

  template<typename T>
  TableWriter& writeCells(std::initializer_list<T> values) {
    for (const auto& value : values) {
      writeCell(value);
    }
    return *this;
  }

  template<typename Iter>
  TableWriter& writeCells(Iter start, Iter end) {
    for (auto iter = start; iter != end; iter++) {
      writeCell(*iter);
    }
    return *this;
  }

  TableWriter& writeCells(const ofVec2f& value) {
    writeCell(value.x);
    writeCell(value.y);
    return *this;
  }

  TableWriter& writeCells(const ofVec3f& value) {
    writeCell(value.x);
    writeCell(value.y);
    writeCell(value.z);
    return *this;
  }

  TableWriter& writeCells(const ofVec4f& value) {
    writeCell(value.x);
    writeCell(value.y);
    writeCell(value.z);
    writeCell(value.w);
    return *this;
  }

  TableWriter& writeCells(const ofMatrix4x4& value) {
    writeCells(value.getRowAsVec4f(0));
    writeCells(value.getRowAsVec4f(1));
    writeCells(value.getRowAsVec4f(2));
    writeCells(value.getRowAsVec4f(3));
    return *this;
  }

  TableWriter& writeBlankCell() {
    beginCell();
    return *this;
  }

  TableWriter& writeBlankCells(std::size_t count) {
    for (auto i = 0; i < count; ++i) {
      writeBlankCell();
    }
    return *this;
  }

  TableWriter& endRow() {
    _out << LINE_SEPARATOR;
    _atRowStart = true;
    _out.flush();
    return *this;
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
