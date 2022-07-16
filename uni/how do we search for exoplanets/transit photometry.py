from manim import *



def intersection_area(big_radius, small_radius, distance_between_centrepoints):
    R=big_radius
    r=small_radius
    d=distance_between_centrepoints
    """Return the area of intersection of two circles.

    The circles have radii R and r, and their centres are separated by d.

    """

    if d <= abs(R-r):
        # One circle is entirely enclosed in the other.
        return np.pi * min(R, r)**2
    if d >= r + R:
        # The circles don't overlap at all.
        return 0

    r2, R2, d2 = r**2, R**2, d**2
    alpha = np.arccos((d2 + r2 - R2) / (2*d*r))
    beta = np.arccos((d2 + R2 - r2) / (2*d*R))
    return ( r2 * alpha + R2 * beta -
             0.5 * (r2 * np.sin(2*alpha) + R2 * np.sin(2*beta))
           )



class TimedAnimationGroup(AnimationGroup):
    '''
    Timed animations may be defined by setting 'start_time' and 'end_time' or 'run_time' in CONFIG of an animation.
    If they are not defined, the Animation behaves like it would in AnimationGroup.
    However, lag_ratio and start_time combined might cause unexpected behavior.
    '''



    def build_animations_with_timings(self):
        """
        Creates a list of triplets of the form
        (anim, start_time, end_time)
        """
        '''
        mostly copied from manimlib.animation.composition (AnimationGroup)
        '''
        self.anims_with_timings = []
        curr_time = 0
        for anim in self.animations:
            # check for new parameters start_time and end_time,
            # fall back to normal behavior if not provided
            try:
                start_time = anim.start_time
                print("ALL SHOULD BE GOOD")
            except:
                start_time = curr_time
                print("SOMETHING WENT WRONG, START TIME OF ANIMATION NOT RECOGNIZED")
            try:
                end_time = anim.end_time
            except:
                end_time = start_time + anim.get_run_time()

            self.anims_with_timings.append(
                (anim, start_time, end_time)
            )
            # Start time of next animation is based on
            # the lag_ratio
            curr_time = interpolate(
                start_time,end_time, self.lag_ratio
            )




            # Start time of next animation is based on
            # the lag_ratio

class Transit(ThreeDScene):
    def construct(self):

        self.camera.background_color=BLACK
        Axes_for_orientation=ThreeDAxes(axis_config={
            "stroke_opacity": 0.2,
            "include_tip": False
        },light_source=ORIGIN)
        self.add(Axes_for_orientation)
        self.set_camera_orientation(phi=65 * DEGREES, theta=30 * DEGREES) #65 30

        star_shell1=Sphere(radius=1/3,checkerboard_colors=[YELLOW_E,YELLOW_E],fill_opacity=1,stroke_opacity=0.2)
        star_shell2 = Sphere(radius=2/3,checkerboard_colors=[YELLOW_E, YELLOW_E], fill_opacity=0.7,stroke_opacity=0.2)
        star_shell3 = Sphere(radius=4/5,checkerboard_colors=[YELLOW_E, YELLOW_E], fill_opacity=0.5,stroke_opacity=0.2)
        Star=VGroup(star_shell1,star_shell2,star_shell3)
        self.renderer.camera.light_source.move_to(ORIGIN)


        planet = Sphere(radius=0.1, checkerboard_colors=[BLACK, BLACK], fill_opacity=1,
                        stroke_opacity=0.2).move_to(np.array([0,2,0]))



        first_orbit = ParametricFunction(
            lambda u: np.array([
                0,
                2 * np.cos(-u),
                2 * np.sin(-u)
            ]), color=None, t_range=np.array([0, 7/2 * PI, 0.01])
        )

        second_orbit = ParametricFunction(
            lambda u: np.array([
                0,
                2 * np.sin(u),
                2 * np.cos(-u)
            ]), color=None, t_range=np.array([0, 5 / 2 * PI, 0.01])
        )

        condition_text=Tex("In order to see an exoplanet in transit, the plane of the orbit has to be aligned with "
                           "our plane of sight.").scale(0.5).rotate(PI/2*np.array([1,0,0])).\
            rotate(PI/2,np.array([0,0,1])).rotate(PI/2,np.array([0,1,0])).shift(3*np.array([0,0,1]))

        self.play(FadeIn(Star,planet))
        anim1=Rotating(Star,np.array([1,1,1]),radians=np.array([4*TAU]),start_time=0,end_time=9.5)
        anim2=MoveAlongPath(planet,first_orbit,start_time=0,end_time=9.5)
        anim3=Write(condition_text,start_time=4,end_time=7)


        Intro_Anim=TimedAnimationGroup(anim1,anim2,anim3)
        self.play(Intro_Anim)



        self.move_camera(phi=0*DEGREES,theta=0*DEGREES)
        self.move_camera(zoom=4)

        ax = Axes(x_length=2.5, y_length=1, x_range=[0, 7], y_range=[1.95, 2.05], tips=False,
                  x_axis_config={
                      # "ticks_included":False
                  },
                  y_axis_config={
                      # "ticks_included":False
                  }
                  ).rotate(-PI * 3 / 2, np.array([0, 0, 1])).shift(1.5 * np.array([0, 0, 1])).shift(
            -0.1 * np.array([0, 1, 0])).shift(0.4 * np.array([1, 0, 0]))


        """ here to the right is positive y direction, up is negativ z direction. For the label objects at least."""

        x_label=Tex("time",color=WHITE).next_to(ax,RIGHT).shift(np.array([0,2.9,-19.5])).rotate(PI/2,np.array([0,0,1])).scale(0.6)
        y_label = Tex("intensity", color=WHITE).next_to(ax, DOWN).rotate(PI*np.array([0,0,1])).scale(0.5).shift(np.array([0,0.4,-1])).scale(0.6)
        description=Tex(r"$I\propto\text{ radiating cross-section } \propto \text{ cross-section of star - cross-section of planet}(t)$",color=WHITE).scale(
            0.4).next_to(y_label,DOWN).rotate(PI/2*np.array([0,0,1])).shift(np.array([-2.5,1,-30]))


        """ Shift the Axis by 1 in y direction: CoSy goes to the right.
            Shift by 1 in x-direction: It goes down by one """

        def transit(transit_time_array,radius_of_planet,radius_of_star,velocity_of_planet):
            #the transit begins end ends when the two projected circles "touch".
            t=transit_time_array
            d_of_t=abs(radius_of_star+radius_of_planet-velocity_of_planet*(t-1.75)) #here i just shifted the graph to the right by 1.8
            Area_of_Star=(radius_of_star)**2*np.pi
            return Area_of_Star-intersection_area(radius_of_star,radius_of_planet,d_of_t)



        zwischenanimation=TimedAnimationGroup(
            FadeOut(Axes_for_orientation,start_time=0,end_time=1),
            Write(ax,start_time=0,end_time=1),Write(x_label,start_time=0,end_time=1),
            Write(y_label,start_time=0,end_time=1),
        )

        self.play(zwischenanimation)

        anim4=Rotating(Star,np.array([1,1,1]),radians=np.array([2*TAU]),start_time=0,end_time=13)
        anim5=MoveAlongPath(planet,second_orbit,start_time=0,end_time=13)
        anim6=Write(description,start_time=3,end_time=6)
        graph=ax.plot(lambda x: transit(x,1/10,4/5,0.45))
        anim7=Write(graph,start_time=7.6,end_time=10)  # Values are doctored in order to have a nice curve

        Second_Anim_Group=TimedAnimationGroup(anim4,anim5,anim6,anim7)
        self.play(Second_Anim_Group)

        #  x direction negative is up
        #  y direction negative is left
        #  z direction positive is front / back

        Group_To_Fade=VGroup(Star,planet,ax,x_label,y_label,description,graph)


        Text=Tex(r"$I \propto R_{star}^2\cdot \pi - A_{planet}(t)$," ,).next_to(description,np.array([1,0,0])).rotate(PI/2,np.array([0,0,1])).shift(np.array([-9,-8,0])).scale(1.7)
        Text0=Tex("where ", r"$A_{pl}(t)$"," is the time-dependent cross-sectional area of the planet blocking starlight.").next_to(description,np.array([1,0,0])).rotate(PI/2,np.array([0,0,1])).shift(np.array([-8.9,0,0])).scale(1.7)

        Text2=Tex(r"$A_{pl}(t)=r_{pl}^2 \cdot cos^{-1}(\frac{d_{pl}}{r_{pl}})-d_1\cdot \sqrt{r_{pl}^2-d_{pl}^2}+r_{star}^2\cdot cos^{-1}(\frac{d_{star}}{r_{star}})-d_{star}\cdot \sqrt{r_{star}^2-d_{star}^2}$,").next_to(
            description,np.array([1,0,0])).rotate(PI/2,np.array([0,0,1])).shift(np.array([-8.2,-8,0])).scale(1.7)
        Text3=Tex("in case the projections overlap in a strict sense, otherwise ", "$0$"," if the don't overlap at all and ",r"$r_{planet}^2\cdot \pi$"," if the completely overlap.").next_to(
            description,np.array([1,0,0])).rotate(PI/2,np.array([0,0,1])).shift(np.array([-7.8,-8.6,0])).scale(1.7)
        Text4=Tex("Other parameters: ", r"$d_{pl}=\frac{r_{pl}^2-r_{star}^2+d^2}{2d}$", " , ",r"$d_{star}=\frac{r_{star}^2-r_{pl}^2+d^2}{2d}$").next_to(
            description,np.array([1,0,0])).rotate(PI/2,np.array([0,0,1])).shift(np.array([-7.4,-8,0])).scale(1.7)
        Text5=Tex("and ",r"$d = \mid (r_{star}+r_{pl}-\text{velocity}_{planet}\cdot t) \mid$. ").next_to(
            description,np.array([1,0,0])).rotate(PI/2,np.array([0,0,1])).shift(np.array([-7,-8,0])).scale(1.7)

        self.play(FadeOut(Group_To_Fade))

        self.set_camera_orientation(zoom=1)


        text_group=VGroup(Text,Text0,Text2,Text3,Text4,Text5).arrange(buff=2).scale(0.4)

        self.play(DrawBorderThenFill(text_group))

        self.wait(3)