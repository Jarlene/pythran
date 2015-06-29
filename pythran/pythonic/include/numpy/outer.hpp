#ifndef PYTHONIC_INCLUDE_NUMPY_OUTER_HPP
#define PYTHONIC_INCLUDE_NUMPY_OUTER_HPP

#include "pythonic/utils/proxy.hpp"
#include "pythonic/types/ndarray.hpp"
#include "pythonic/builtins/None.hpp"
#include "pythonic/numpy/asarray.hpp"

namespace pythonic
{

  namespace numpy
  {
    template <class T0, size_t N0, class T1, size_t N1>
    types::ndarray<decltype(std::declval<T0>() + std::declval<T1>()), 2>
    outer(types::ndarray<T0, N0> const &a, types::ndarray<T1, N1> const &b);

    template <class T0, size_t N0, class E1>
    auto outer(types::ndarray<T0, N0> const &a, E1 const &b)
        -> decltype(outer(a, asarray(b)));

    template <class E0, class T1, size_t N1>
    auto outer(E0 const &a, types::ndarray<T1, N1> const &b)
        -> decltype(outer(asarray(a), b));

    template <class E0, class E1>
    auto outer(E0 const &a, E1 const &b)
        -> decltype(outer(asarray(a), asarray(b)));

    PROXY_DECL(pythonic::numpy, outer);
  }
}

#endif
