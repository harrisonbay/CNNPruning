import {BaseObject, copy, flat, get, id, init, set} from './__util__';
import {_selref} from './_selref';

class SelectInterval extends BaseObject {

  constructor(...args) {
    super();
    init(this);
    set(this, "type", "interval");
    this["_sel"] = args[0] !== undefined ? args[0] : id("sel");
  }

  bind(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "bind", value);
      return obj;
    } else {
      return get(this, "bind");
    }
  }

  clear(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "clear", value);
      return obj;
    } else {
      return get(this, "clear");
    }
  }

  empty(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "empty", value);
      return obj;
    } else {
      return get(this, "empty");
    }
  }

  encodings(...value) {
    if (arguments.length) {
      const obj = copy(this);
      value = flat(value);
      set(obj, "encodings", value);
      return obj;
    } else {
      return get(this, "encodings");
    }
  }

  fields(...value) {
    if (arguments.length) {
      const obj = copy(this);
      value = flat(value);
      set(obj, "fields", value);
      return obj;
    } else {
      return get(this, "fields");
    }
  }

  init(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "init", value);
      return obj;
    } else {
      return get(this, "init");
    }
  }

  mark(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "mark", value);
      return obj;
    } else {
      return get(this, "mark");
    }
  }

  on(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "on", value);
      return obj;
    } else {
      return get(this, "on");
    }
  }

  resolve(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "resolve", value);
      return obj;
    } else {
      return get(this, "resolve");
    }
  }

  translate(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "translate", value);
      return obj;
    } else {
      return get(this, "translate");
    }
  }

  type(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "type", value);
      return obj;
    } else {
      return get(this, "type");
    }
  }

  zoom(value) {
    if (arguments.length) {
      const obj = copy(this);
      set(obj, "zoom", value);
      return obj;
    } else {
      return get(this, "zoom");
    }
  }

  key(...values) {
    let obj = _selref(this["_sel"]);
    return obj.key(...values);
  }

  field(...values) {
    let obj = _selref(this["_sel"]);
    return obj.field(...values);
  }

  encoding(...values) {
    let obj = _selref(this["_sel"]);
    return obj.encoding(...values);
  }

  toObject(flag) {
    return flag ? {[this["_sel"]]: super.toObject()} : {selection: this["_sel"]};
  }

}

export function selectInterval(...args) {
  return new SelectInterval(...args);
}