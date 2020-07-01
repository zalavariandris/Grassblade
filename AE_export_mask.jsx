var project = app.project;
var comp = project.activeItem;
var frameRate = comp.frameRate;
// get first layer
var layer = comp.layer(1);

// get masks
var masks = layer.property("Masks");
var numMasks = masks.numProperties;

var mainString = "";
mainString+="{\n";

for(var i=1; i<=numMasks;i++){
    var maskProperty = masks(i);
    mainString+='"'+maskProperty.name+'":{\n';
    var path = maskProperty.property("Mask Path");
    var numKeys = path.numKeys;
    for(var key=0; key<numKeys; key++){
        var time = path.keyTime(key+1);
        var shape = path.keyValue(key+1);
        var vertices = shape.vertices;
        var inTangents = shape.inTangents;
        var outTangents = shape.outTangents;
        
        var frame = time*frameRate;
        mainString+='\t"'+parseInt(frame)+'":{\n';
        mainString+='\t\t"vertices": [' +vertices.join(', ')+'],\n'
        mainString+='\t\t"inTangents": [' +inTangents.join(', ')+'],\n'
        mainString+='\t\t"outTangents": [' +outTangents.join(', ')+']\n'
        if(key<numKeys-1){
            mainString+='\t}'+','+'\n';
        }else{
            mainString+='\t}\n';
        }
        
    }
    if(i<=numMasks-1){
        mainString+='}'+','+'\n';
    }else{
        mainString+='}\n';
    }
}
line = "}"
mainString +=line;
  
var myFile = new File("~/Desktop/mask.json");
myFile.open("w")
myFile.encoding = "UTF-8";
myFile.write(mainString);
myFile.close();
