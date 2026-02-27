

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    username TEXT UNIQUE,
    bio TEXT,
    skills TEXT[], -- Array of skills
    student_id TEXT,
    university TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);


CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    budget DECIMAL(10, 2) NOT NULL CHECK (budget >= 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')),
    creator_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    deadline TIMESTAMP WITH TIME ZONE,
    tags TEXT[], -- Array of tags for better searchability
    attachments JSONB, -- Store attachment URLs/metadata as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);


CREATE TABLE IF NOT EXISTS public.task_applications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE NOT NULL,
    applicant_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    message TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(task_id, applicant_id) -- One application per user per task
);

CREATE TABLE IF NOT EXISTS public.ratings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE NOT NULL,
    rated_user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    rater_user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(task_id, rated_user_id, rater_user_id)
);


-- Index for fetching user's created tasks
CREATE INDEX IF NOT EXISTS idx_tasks_creator_id ON public.tasks(creator_id);

-- Index for fetching assigned tasks
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON public.tasks(assigned_to);

-- Index for filtering by status
CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks(status);

-- Index for filtering by category
CREATE INDEX IF NOT EXISTS idx_tasks_category ON public.tasks(category);

-- Index for text search on title
CREATE INDEX IF NOT EXISTS idx_tasks_title ON public.tasks USING gin(to_tsvector('english', title));

-- Index for text search on description
CREATE INDEX IF NOT EXISTS idx_tasks_description ON public.tasks USING gin(to_tsvector('english', description));

-- Index for created_at for sorting
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON public.tasks(created_at DESC);

-- Index for task applications
CREATE INDEX IF NOT EXISTS idx_task_applications_task_id ON public.task_applications(task_id);
CREATE INDEX IF NOT EXISTS idx_task_applications_applicant_id ON public.task_applications(applicant_id);

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ratings ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
-- Users can view all profiles
CREATE POLICY "Profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    USING (true);

-- Users can insert their own profile
CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Tasks Policies
-- Anyone can view open tasks
CREATE POLICY "Open tasks are viewable by everyone"
    ON public.tasks FOR SELECT
    USING (true);

-- Authenticated users can create tasks
CREATE POLICY "Authenticated users can create tasks"
    ON public.tasks FOR INSERT
    WITH CHECK (auth.uid() = creator_id);

-- Task creators can update their own tasks
CREATE POLICY "Users can update their own tasks"
    ON public.tasks FOR UPDATE
    USING (auth.uid() = creator_id);

-- Task creators can delete their own tasks
CREATE POLICY "Users can delete their own tasks"
    ON public.tasks FOR DELETE
    USING (auth.uid() = creator_id);

-- Task Applications Policies
-- Users can view applications for their tasks or their own applications
CREATE POLICY "Users can view relevant applications"
    ON public.task_applications FOR SELECT
    USING (
        auth.uid() = applicant_id OR
        auth.uid() IN (SELECT creator_id FROM public.tasks WHERE id = task_id)
    );

-- Users can create applications
CREATE POLICY "Users can create applications"
    ON public.task_applications FOR INSERT
    WITH CHECK (auth.uid() = applicant_id);

-- Users can update their own applications
CREATE POLICY "Users can update their own applications"
    ON public.task_applications FOR UPDATE
    USING (auth.uid() = applicant_id);

-- Ratings Policies
-- Everyone can view ratings
CREATE POLICY "Ratings are viewable by everyone"
    ON public.ratings FOR SELECT
    USING (true);

-- Users can create ratings for completed tasks they were part of
CREATE POLICY "Users can create ratings"
    ON public.ratings FOR INSERT
    WITH CHECK (auth.uid() = rater_user_id);

-- Function to automatically create a profile when a user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, username, bio, skills, student_id, university)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'username',
        NEW.raw_user_meta_data->>'bio',
        CASE
            WHEN NEW.raw_user_meta_data->'skills' IS NOT NULL
            THEN ARRAY(SELECT jsonb_array_elements_text(NEW.raw_user_meta_data->'skills'))
            ELSE NULL
        END,
        NEW.raw_user_meta_data->>'student_id',
        NEW.raw_user_meta_data->>'university'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call handle_new_user function after user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to update updated_at on all tables
DROP TRIGGER IF EXISTS set_profiles_updated_at ON public.profiles;
CREATE TRIGGER set_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS set_tasks_updated_at ON public.tasks;
CREATE TRIGGER set_tasks_updated_at
    BEFORE UPDATE ON public.tasks
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- Create storage bucket for task attachments
INSERT INTO storage.buckets (id, name, public)
VALUES ('task-attachments', 'task-attachments', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for task attachments
CREATE POLICY "Task attachments are publicly accessible"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'task-attachments');

CREATE POLICY "Authenticated users can upload task attachments"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'task-attachments' AND
        auth.role() = 'authenticated'
    );
