
#inlcude <math.h>


typedef struct {
  double sin_delta;
  double cos_delta;
  double cos_delta2;
} Metric;


void metric_init(Metric *m, double x0, double y0) {

  double theta = y0/180.*3.1415926;

  m->sin_delta = sin(theta);
  m->cos_delta = cos(theta);
  m->cos_delta2 = m->cos_delta * m->cos_delta;

}


double metric_distance2(Metric *m, double x1, double y1, double x2, double y2) {
  double dx = (x2-x1);
  double dy = (y2-y1);

  return (dx*dx*cos_delta2 + dy*dy)
}


void metric_rotate(Metric *m, double x1, double y1, double *x2, double *y2) {

}



typedef struct {
  double g_x;
  double g_y;
} Metric;


void metric_init(Metric *m, double x0, double y0) {

  double theta = y0/180.*3.1415926;

  m->g_x = cos(theta);
  m->g_y = 1.;

}


double metric_distance2(Metric *m, double x1, double y1, double x2, double y2) {
  double dx = (x2-x1);
  double dy = (y2-y1);

  return ((dx*g_x)^2 + (dy*g_y)^2);
}






#define DISTANCE( x0, y0, x1, y1, x2, y2, d ) ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))
#define ROTATE( x0, y0, x1, y1, angle, x2, y2) 
