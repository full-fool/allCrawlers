<php  $str = 'ippr_z2C$qAzdH3FAzdH3Fojgojg_z&e3Bf5f5_z&e3Bv54AzdH3FrAzdH3Fda8a8a8nAzdH3Fda8a8a8n8m9bdc-8a0abn8cdb_z&e3B3r2'; 
function uncomplie($k){     
$c = array('_z2C$q','_z&e3B','AzdH3F');    
$d = array(
'a'=> "0",
'b'=> "8",
'c'=> "5",
'd'=> "2",
'e'=> "v",
'f'=> "s",
'g'=> "n",
'h'=> "k",
'i'=> "h",
'j'=> "e",
'k'=> "b",
'l'=> "9",
'm'=> "6",
'n'=> "3",
'o'=> "w",
'p'=> "t",
'q'=> "q",
'r'=> "p",
's'=> "l",
't'=> "i",
'u'=> "f",
'v'=> "c",
'w'=> "a",
"0"=> "7",
'1'=> "d",
'2'=> "g",
'3'=> "j",
'4'=> "m",
"5"=> "o",
"6"=> "r",
"7"=> "u",
"8"=> "1",
"9"=> "4",
'_z2C$q'=> ":",
'_z&e3B'=> ".",
'AzdH3F'=> "/"
);
    if(!$k || strpos($k, "http"))
        return $k;
    $j = $k;
    foreach ($c as $value) {
        $j = str_replace($value,$d[$value],$j);
    }
    $arr = str_split($j);
    foreach ($arr as $k=>$v) {
        if(preg_match('/^[a-w\d]+$/',$v))
            $arr[$k] = $d[$v];
    }
    return implode('',$arr);
}




print_r(uncomplie($str));


test = '_d_z&e3B3r2'
http://pic4.nipic.com/20090929/3346396?230806016598