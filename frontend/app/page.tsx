"use client";

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

// Define the Project type
interface Project {
  id: string | number;
  name: string;
  description: string | null;
  admin_name: string;
  repo_url: string;
  tech_stack: string[];
  open_issues: number;
  closed_issues: number;
  open_assigned_issues: number;
  closed_assigned_issues: number;
  health_score: number;
}

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTech, setSelectedTech] = useState("All");
  const [loading, setLoading] = useState(true);
  const [visibleCount, setVisibleCount] = useState(9); // Initial projects to show

  useEffect(() => {
    // 1. Initial Data Fetch function defined
    async function fetchProjects() {
      const { data, error } = await supabase
        .from('gssoc_projects')
        .select('*')
        .order('health_score', { ascending: false });

      if (!error && data) setProjects(data);
      setLoading(false);
    }

    fetchProjects();

    // 2. MAGIC: Real-time Listener (Auto-updates UI)
    const subscription = supabase
      .channel('live-updates')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'gssoc_projects' }, (payload) => {
        console.log('Database updated! Refreshing UI automatically...', payload);
        fetchProjects();
      })
      .subscribe();

    return () => {
      supabase.removeChannel(subscription);
    };
  }, []);

  // Filter Logic: Search match (name or description) AND Tech Stack match
  const filteredProjects = projects.filter((p) => {
    const matchesSearch = 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()));
      
    const matchesTech = selectedTech === "All" || (p.tech_stack && p.tech_stack.includes(selectedTech));
    
    return matchesSearch && matchesTech;
  });

  const visibleProjects = filteredProjects.slice(0, visibleCount); 

  // Extract unique tech stacks for the dropdown
  const allTechStacks = Array.from(new Set(projects.flatMap(p => p.tech_stack || [])));

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6 md:p-10 font-sans">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-linear-to-r from-green-400 to-blue-500">
          GSSoC Radar 🎯
        </h1>
        <p className="text-gray-400 mb-8">Deep analytics & project recommendation engine for contributors.</p>

        {/* Filters & Search Bar */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <input 
            type="text" 
            placeholder="Search projects or descriptions (e.g., Healthcare, AI)..." 
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <select 
            className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500"
            value={selectedTech}
            onChange={(e) => setSelectedTech(e.target.value)}
          >
            <option value="All">All Tech Stacks</option>
            {allTechStacks.map(tech => (
              <option key={tech as string} value={tech as string}>{tech as string}</option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="text-center text-gray-400 mt-20">Loading project data...</div>
        ) : (
          <>
            {/* Project Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {visibleProjects.map((project) => (
                <div key={project.id} className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg hover:border-gray-700 transition flex flex-col justify-between">
                  <div>
                    <h2 className="text-xl font-semibold mb-1 truncate" title={project.name}>{project.name}</h2>
                    <p className="text-sm text-gray-400 mb-4">Admin: <span className="text-blue-400">{project.admin_name}</span></p>
                    
                    {/* Tech Stack Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {project.tech_stack?.slice(0, 3).map((tech: string) => (
                        <span key={tech} className="bg-gray-800 text-xs text-gray-300 px-2 py-1 rounded-md border border-gray-700">
                          {tech}
                        </span>
                      ))}
                    </div>
                    
                    {project.description && (
                       <p className="text-xs text-gray-500 mb-6 line-clamp-2">{project.description}</p>
                    )}

                    <div className="grid grid-cols-2 gap-3 mb-6">
                      <div className="bg-gray-800/50 p-2 rounded-lg border border-gray-800 text-center">
                        <p className="text-[10px] text-gray-400">Total Opened</p>
                        <p className="text-md font-bold text-gray-200">{project.open_issues}</p>
                      </div>
                      <div className="bg-gray-800/50 p-2 rounded-lg border border-gray-800 text-center">
                        <p className="text-[10px] text-gray-400">Total Closed</p>
                        <p className="text-md font-bold text-gray-200">{project.closed_issues}</p>
                      </div>
                      <div className="bg-green-900/20 p-2 rounded-lg border border-green-900/30 text-center">
                        <p className="text-[10px] text-green-400">Open & Assigned</p>
                        <p className="text-md font-bold text-green-400">{project.open_assigned_issues}</p>
                      </div>
                      <div className="bg-blue-900/20 p-2 rounded-lg border border-blue-900/30 text-center">
                        <p className="text-[10px] text-blue-400">Closed Assigned</p>
                        <p className="text-md font-bold text-blue-400">{project.closed_assigned_issues}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="pt-4 border-t border-gray-800 flex justify-between items-center">
                      <span className="text-sm text-gray-400">Activity Health</span>
                      <span className="text-2xl font-bold text-yellow-400">{project.health_score}%</span>
                    </div>
                    
                    <a 
                      href={project.repo_url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="mt-4 block w-full text-center bg-white text-black py-2 rounded-lg font-semibold hover:bg-gray-200 transition"
                    >
                      View Repository
                    </a>
                  </div>
                </div>
              ))}
              
              {filteredProjects.length === 0 && (
                <div className="col-span-full text-center text-gray-500 py-10">
                  No projects match your search criteria.
                </div>
              )}
            </div>

            {/* Load More Button */}
            {visibleCount < filteredProjects.length && (
              <div className="flex justify-center mt-12 mb-4">
                <button 
                  onClick={() => setVisibleCount((prev) => prev + 9)}
                  className="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white font-bold py-3 px-8 rounded-full transition-all shadow-lg"
                >
                  Load More Projects ({filteredProjects.length - visibleCount} remaining)
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}