#ifndef PYTHONIC_INCLUDE_TYPES_FLOAT_HPP
#define PYTHONIC_INCLUDE_TYPES_FLOAT_HPP

#include "pythonic/types/attr.hpp"
#include <cstddef>

namespace pythonic
{
  namespace builtins
  {
    template <size_t AttributeID>
    double getattr(double self);
  }
}

#endif
