<!DOCTYPE html>
<html>
<body>

<h2>My First JavaScript</h2>

<table>
	<tr>
    	<td>Point N°</td>
        <td>X</td>
        <td>Y</td>
        <td>Z</td>
        <td>R</td>
    </tr>
	<tr>
    	<td>1</td>
        <td><input id="x1" value="0" /></td>
        <td><input id="y1" value="24" /></td>
        <td><input id="z1" value="0" /></td>
        <td><input id="r1" value="12" /></td>
    </tr>
	<tr>
    	<td>2</td>
        <td><input id="x2" value="24" /></td>
        <td><input id="y2" value="0" /></td>
        <td><input id="z2" value="0" /></td>
        <td><input id="r2" value="11" /></td>
    </tr>
	<tr>
    	<td>3</td>
        <td><input id="x3" value="15" /></td>
        <td><input id="y3" value="15" /></td>
        <td><input id="z3" value="0" /></td>
        <td><input id="r3" value="14" /></td>
    </tr>
</table>

<button type="button" onclick="calculate()">Calculate</button>

<p id="result"></p>

<script>
/*	
	Find the intersection(s) (x,y,z) and (x_,y_,z_) of three spheres centered
	at (x1,y1,z1), (x2,y2,z2) and (x3,y3,z3) with corresponding radii of r1, r2, and r3
	
	Adapted from http://mathforum.org/library/drmath/view/64311.html
*/

function intersect3spheres(x1, x2, x3, y1, y2, y3, z1, z2, z3, r1, r2, r3) {

	var a1, b1, c1, k1, a3, b3, c3, k3, a31, b31, 
		e, f, g, h, A, B, C, x, y, z, x_, y_, z_, rootD;
/*
	Three spheres:
	EQ1: (x1 - x)^2 + (y1 - y)^2 + (z1 - z)^2 = r1^2
	EQ2: (x2 - x)^2 + (y2 - y)^2 + (z2 - z)^2 = r2^2
	EQ3: (x3 - x)^2 + (y3 - y)^2 + (z3 - z)^2 = r3^2	
	
	1. Pick one of the equations (EQ2) and subtract it from the other two (EQ1, EQ3).
	That will make those other two equations into linear equations in the three unknowns.  
*/
	
	// Subtract EQ2 from EQ1, move all constants to right side
	// Call the right side constant k1
	k1 = r1 * r1 - r2 * r2 - x1 * x1 + x2 * x2 - y1 * y1 + y2 * y2 - z1 * z1 + z2 * z2;
    console.log('k1', k1);
	
	// Left side of EQ1 is of the form a1x + b1y + c1z
	// where a1, b1, and c1 are the coefficients	
	a1 = 2 * (x2 - x1);
	b1 = 2 * (y2 - y1);	
	c1 = 2 * (z2 - z1);
    console.log('a1', a1);
    console.log('b1', b1);
    console.log('c1', c1);
	
	// Subtract EQ2 from EQ3, move all constants to right side
	// Call the right side constant k3
	k3 = r3 * r3 - r2 * r2 - x3 * x3 + x2 * x2 - y3 * y3 + y2 * y2 - z3 * z3 + z2 * z2;
    console.log('k3', k3);
	
	// Left side of EQ3 is of the form a3x + b3y + c3z
	// where a3, b3, and c3 are the coefficients		
	a3 = 2 * (x2 - x3);
	b3 = 2 * (y2 - y3);
	c3 = 2 * (z2 - z3);
    console.log('a3', a3);
    console.log('b3', b3);
    console.log('c3', c3);
	
	// The two equations (EQ1, EQ3) are now linear equations in the three unknowns:
	// EQ1: a1x + b1y + c1z = k1
	// EQ3: a3x + b3y + c3z = k3	
		
		
/*	
	2. Use them to find two of the variables (x, y) as linear expressions in the
	third (z).  These two equations are those of a line in 3-space, which
	passes through the two points of intersection of the three spheres. 
*/

	// Find y as a linear expression of z.
	// y = ez + f
	
	if (a1 === 0) {
	
		// y = -(c1/b1)z + k1/b1
		e = -c1 / b1;
		f = k1 / b1;
		
	} else if (a3 === 0) {
	
		// y = -(c3/b3)z + k3/b3
		e = -c3 / b3;
		f = k3 / b3;		
		
	} else {

		// If a1 and a3 are non-zero:
		// Multiply EQ1 by a3 / a1, then subtract EQ3 from it.
		// This gives a new equation with coefficients 
	
		a31 = a3 / a1;
		
		// Subtract equations, x term cancels out. Left with:
		// (a31 * b1 - b3)y + (a31 * c1 - c3)z = a31 * k1 - k3
		
		e = - ((a31 * c1 - c3) / (a31 * b1 - b3));
		f = (a31 * k1 - k3) / (a31 * b1 - b3);
	
	}
    console.log('a31', a31);
    console.log('e', e);
    console.log('f', f);

	// Find x as a linear expression of z.
	// x = gz + h		
	
	if (b1 === 0) {
	
		g = -c1 / a1;
		h = k1 / a1;
		
	} else if (b3 === 0) {
	
		g = -c3 / a3;
		h = k3 / a3;
		
	} else {

		// If b1 and b3 are non-zero:
		// Multiply EQ1 by b3 / b1, then subtract EQ3 from it.
		// This gives a new equation with coefficients 
	
		b31 = b3 / b1;
		
		// Subtract equations, y term cancels out. Left with:
		// (b31 * a1 - a3)x + (b31 * c1 - c3)z = b31 * k1 - k3
		
		g = - ((b31 * c1 - c3) / (b31 * a1 - a3));
		h = (b31 * k1 - k3) / (b31 * a1 - a3);
	}
    console.log('b31', b31);
    console.log('g', g);
    console.log('h', h);
	
/*	
	3. Then substitute these into the equation of any of the original
	spheres (EQ1).  This will give you a quadratic equation in one variable,
	which you can solve to find the two roots.  
	EQ1: (x1 - x)^2 + (y1 - y)^2 + (z1 - z)^2 = r1^2
	EQ1: (x1 - gz - h)^2 + (y1 - ez - f)^2 + (z1 - z)^2 = r1^2
	
	x1^2 - x1gz - x1h - x1gz + g^2 * z^2 + ghz - x1h + ghz + h^2 +
	y1^2 - y1ez - y1f - y1ez + e^2 * z^2 + efz - y1f + efz + f^2 +
	z1^2 - 2z1z + z^2
	= r1^2
	Simplify and put in quadratic form of Az^2 + Bz + C = 0
	
	x1^2 + y1^2 + z1^2 - x1h - y1f - x1h - y1f + h^2 + f^2
	- x1gz - y1ez - 2z1z - x1gz - y1ez + ghz + efz + ghz + efz
	+ g^2 * z^2 + e^2 * z^2 + z^2
	= r1^2
	 
	x1^2 + y1^2 + z1^2 - x1h - y1f - x1h - y1f + h^2 + f^2 - r1^2
	+ (- x1g- y1e - 2z1 - x1g - y1e + gh + ef + gh + ef) * z
	+ (g^2 + e^2 + 1) * z^2
	= 0
*/	

	A = g * g + e * e + 1;
	B = -x1 * g - y1 * e - 2 * z1 - x1 * g - y1 * e + 2 * g * h + 2 * e * f;
	C = x1 * x1 + y1 * y1 + z1 * z1 - 2 * x1 * h - 2 * y1 * f + h * h + f * f - r1 * r1;
    console.log('A', A);
    console.log('B', B);
    console.log('C', C);
	
	// Quadratic formula: z = (-B +- sqrt(B^2 - 4AC)) / 2A
	// Use the quadratic formula to solve to find the two roots.
	
	rootD = Math.sqrt(B * B - 4 * A * C);
    console.log('rootD=Math.sqrt(', B, '*', B, '- 4*', A, '*', C, ')');
    console.log('rootD', rootD);
	
	z = (-B + rootD) / (2 * A);
	z_ = (-B - rootD) / (2 * A);
    console.log('z', z);
    console.log('z_', z_);

/*	
	4. These values will allow you to determine the corresponding values of
	the other two variables, giving you the coordinates of the two
	intersection points.	
*/
		
	x = g * z + h;
	x_ = g * z_ + h;
    console.log('x', x);
    console.log('x_', x_);
	
	y = e * z + f;
	y_ = e * z_ + f;
    console.log('y', y);
    console.log('y_', y_);
	
	return [x, y, z, x_, y_, z_];
}

function calculate() {
	x1 = parseInt(document.getElementById('x1').value, 10);
    y1 = parseInt(document.getElementById('y1').value, 10);
    z1 = parseInt(document.getElementById('z1').value, 10);
    r1 = parseInt(document.getElementById('r1').value, 10);
    console.log('point 1 [' + x1 + ', ' + y1 + ', ' + z1 + '] r=' + r1); 
        
    x2 = parseInt(document.getElementById('x2').value, 10);
   	y2 = parseInt(document.getElementById('y2').value, 10);
    z2 = parseInt(document.getElementById('z2').value, 10);
    r2 = parseInt(document.getElementById('r2').value, 10);
    console.log('point 2 [' + x2 + ', ' + 2 + ', ' + z2 + '] r=' + r2); 
    
    x3 = parseInt(document.getElementById('x3').value, 10);
    y3 = parseInt(document.getElementById('y3').value, 10);
    z3 = parseInt(document.getElementById('z3').value, 10);
    r3 = parseInt(document.getElementById('r3').value, 10);
    console.log('point 3 [' + x3 + ', ' + y3 + ', ' + z3 + '] r=' + r3); 
    
	document.getElementById('result').innerHTML = intersect3spheres(x1, x2, x3, y1, y2, y3, z1, z2, z3, r1, r2, r3)
}

</script>

</body>
</html> 
