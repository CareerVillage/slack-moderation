class nginx::apt {
  apt::source { "nginx":
    location => "http://nginx.org/packages/ubuntu/",
    release => "trusty",
    key => 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62,
    repos => "nginx";
  }
}
