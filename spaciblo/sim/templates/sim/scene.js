
//
// GLGE Extensions
//
GLGE.Group.prototype.getUserGroup = function(username){
   for(var i=0; i < this.children.length; i++){
      if(username == this.children[i].username) return this.children[i];
      if(typeof this.children[i].getUserGroup != "undefined"){
         var result = this.children[i].getUserGroup(username);
         if(result != null) return result;
      }
   }
   return null;
}

GLGE.Scene.prototype.getUserGroup = GLGE.Group.prototype.getUserGroup;