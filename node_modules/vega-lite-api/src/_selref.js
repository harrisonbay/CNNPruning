import {BaseObject, copy, get, init, set} from './__util__';

class _Selref extends BaseObject {

  constructor(...args) {
    super();
    init(this);
    if (args[0] !== undefined) set(this, "selection", args[0]);
  }

  key(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "key", value);
      return obj;
    } else {
      return get(this, "key");
    }
  }

  field(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "field", value);
      return obj;
    } else {
      return get(this, "field");
    }
  }

  encoding(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "encoding", value);
      return obj;
    } else {
      return get(this, "encoding");
    }
  }

}

export function _selref(...args) {
  return new _Selref(...args);
}