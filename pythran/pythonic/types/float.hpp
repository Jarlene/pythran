#ifndef PYTHONIC_TYPES_FLOAT_HPP
#define PYTHONIC_TYPES_FLOAT_HPP

#include "pythonic/include/types/float.hpp"

#include "pythonic/types/attr.hpp"
#include <cstddef>

namespace pythonic
{
  namespace builtins
  {
    template <size_t AttributeID>
    double getattr(double self)
    {
      return AttributeID == pythonic::types::attr::REAL ? self : 0.;
    }
  }
}

#endif
