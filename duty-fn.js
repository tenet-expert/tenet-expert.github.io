    function stockBlob(c){
      if(!c) return "";
      return [c.invoice,c.note,c.lease,c.tag,c.marks,c.label].map(x=>String(x||"")).join(" ").toLowerCase();
    }
